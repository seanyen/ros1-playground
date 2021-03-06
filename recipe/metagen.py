import ruamel.yaml
import subprocess
import rospkg
import rosdep2
import os
import catkin_pkg.package
import json
import datetime
import copy

yaml = ruamel.yaml.YAML()
yaml.indent(mapping=2, sequence=4, offset=2)

def convert_os_override_option():
    return 'conda', '10'

try:
    # json_result = subprocess.check_output('conda search --override-channels -c ros-playground/label/staging ros-%s --json' % os.environ['ROS_DISTRO'], shell=True, stderr=subprocess.STDOUT)
    json_result = subprocess.check_output('conda search ros-%s --json' % os.environ['ROS_DISTRO'], shell=True, stderr=subprocess.STDOUT)
except subprocess.CalledProcessError as e:
    json_result = e.output
packages_released = json.loads(json_result)
#packages_released = {}

packages_skipped = [
    'rmw_cyclonedds_cpp',
    'rmw_opensplice_cpp',
    'rmw_connext_cpp',
    'gmock_vendor',
    'gtest_vendor',
    'libyaml_vendor',
    'connext_cmake_module',
    'opensplice_cmake_module',
    'rosidl_typesupport_connext_c',
    'rosidl_typesupport_connext_cpp',
    'rosidl_typesupport_opensplice_cpp',
    'rosidl_typesupport_opensplice_c',
    'test_msgs',
    'rttest',
    'tlsf',
    'tlsf_cpp',
    'pendulum_control']

rospack = rospkg.RosPack()

source_cache_dir = rosdep2.sources_list.get_sources_cache_dir()

sources_loader = rosdep2.sources_list.SourcesListLoader.create_default(sources_cache_dir=source_cache_dir, os_override=convert_os_override_option())

lookup = rosdep2.lookup.RosdepLookup.create_from_rospkg(rospack=rospack, sources_loader=sources_loader)
view = lookup.get_rosdep_view(rosdep2.rospkg_loader.DEFAULT_VIEW_KEY)

installer_context = rosdep2.create_default_installer_context()
installer_context.set_os_override('conda', '10')

def _resolve(pkg):
    resolved = []
    try:
        d = view.lookup(pkg)
        os_name, os_version = installer_context.get_os_name_and_version()
        rule_installer, rule = d.get_rule_for_platform(
            os_name, os_version,
            installer_context.get_os_installer_keys(os_name),
            installer_context.get_default_os_installer_key(os_name))

        installer = installer_context.get_installer(rule_installer)
        resolved = installer.resolve(rule)
    except:
        pass
    if len(resolved) == 0:
        return ['ros-%s-%s' % (os.getenv('ROS_DISTRO'), pkg.replace("_", "-")) ]
    return resolved

source = []
with open("ros.rosinstall", 'r') as stream:
    data = yaml.load(stream)
    for repo in data:
        entry = {}
        pkg_name = ""
        if 'tar' in repo:
            local_name = repo['tar']['local-name']
            entry['url'] = repo['tar']['uri']
        if 'git' in repo:
            local_name = repo['git']['local-name']
            entry['git_url'] = repo['git']['uri']
            entry['git_rev'] = repo['git']['version']
        local_rospack = rospkg.RosPack([os.path.join('src', local_name)])
        for pkg_shortname in local_rospack.list():
            local_entry = copy.deepcopy(entry)
            pkg_name = _resolve(pkg_shortname)[0]
            local_entry['folder'] = '%s/src/work' % pkg_name
            if pkg_name in packages_released:
                continue
            location_to_test = os.path.join(os.getenv('CURRENT_PATH'), 'patch', '%s.patch' % pkg_name)
            if os.path.exists(location_to_test):
                local_entry['patches'] = [ 'patch/%s.patch' % pkg_name ]
            source.append(local_entry)

unsatisfied_deps = set()
outputs = []
for pkg_shortname in rospack.list():
    pkg_name = _resolve(pkg_shortname)[0]
    manifest = rospack.get_manifest(pkg_shortname)
    if pkg_name in packages_released:
        continue
    output = {
        'name': pkg_name,
        'version': manifest.version,
        'requirements': {
            'build': [
                "{{ compiler('cxx') }}",
                "{{ compiler('c') }}",
                "ninja",
                "cmake"
            ],
            'host': ['colcon-common-extensions', 'python {{ python }}'],
            'run': ['python {{ python }}']
        }
    }
    package_uri = rospack.get_path(pkg_shortname)
    pkg = catkin_pkg.package.parse_package('%s\\package.xml' % package_uri)
    pkg.evaluate_conditions(os.environ)

    if 'cmake' == pkg.get_build_type():
        print('cmake %s' % pkg_shortname)
        continue
    build_deps = pkg.build_depends + pkg.buildtool_depends + pkg.build_export_depends + pkg.buildtool_export_depends + pkg.test_depends
    build_deps = [d.name for d in build_deps if d.evaluated_condition]
    build_deps = set(build_deps)

    for dep in build_deps:
        if dep in packages_skipped:
            continue
        resolved_dep = _resolve(dep)
        if not resolved_dep:
            unsatisfied_deps.add(dep)
            continue
        # if resolved_dep[0].startswith('ros-') and not dep in rospack.list():
        #    continue
        output['requirements']['host'].extend(resolved_dep)

    run_deps = pkg.run_depends + pkg.exec_depends + pkg.build_export_depends + pkg.buildtool_export_depends
    run_deps = [d.name for d in run_deps if d.evaluated_condition]
    run_deps = set(run_deps)

    for dep in run_deps:
        if dep in packages_skipped:
            continue
        resolved_dep = _resolve(dep)
        if not resolved_dep:
            unsatisfied_deps.add(dep)
            continue
        # if resolved_dep[0].startswith('ros-') and not dep in rospack.list():
        #    continue
        output['requirements']['run'].extend(resolved_dep)

    if pkg_shortname == 'foonathan_memory_vendor':
        output['requirements']['run'].append('foonathan-memory')
        output['requirements']['host'].append('foonathan-memory')

    if pkg_shortname == 'rmw_implementation':
        output['requirements']['run'].extend(_resolve('rmw_fastrtps_cpp'))
        output['requirements']['host'].extend(_resolve('rmw_fastrtps_cpp'))

    output['requirements']['run'] = list(set(output['requirements']['run']))
    output['requirements']['host'] = list(set(output['requirements']['host']))

    output['script'] = 'bld_colcon.bat'
    outputs.append(output)

print(unsatisfied_deps)

template = """\
package:
  name: ros
  version: 0.0.1

source:

build:
  number: 0
  skip: true  # [not win64]

outputs:

about:
  home: https://www.ros.org/
  license: BSD-3-Clause
  summary: |
    Robot Operating System

extra:
  recipe-maintainers:
    - seanyen
"""

meta = yaml.load(template)

meta['source'] = source
meta['outputs'] = outputs
meta['package']['version'] = f"{datetime.datetime.now():%Y.%m.%d}"

with open("meta.yaml", 'w') as stream:
    yaml.dump(meta, stream)
