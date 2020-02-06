import ruamel.yaml
import subprocess
import rospkg
import rosdep2
import os
import catkin_pkg.package

yaml = ruamel.yaml.YAML()
yaml.indent(mapping=2, sequence=4, offset=2)

def convert_os_override_option():
    return 'conda', '10'

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
    return resolved

source = []
with open("ros.rosinstall", 'r') as stream:
    data = yaml.load(stream)
    for repo in data:
        entry = {}
        if 'tar' in repo:
            local_name = repo['tar']['local-name']
            pkg_name = _resolve(local_name)[0]
            entry['url'] = repo['tar']['uri']
            entry['folder'] = pkg_name
            entry['fn'] = "%s.tar.gz" % pkg_name
        if 'git' in repo:
            local_name = repo['git']['local-name']
            pkg_name = _resolve(local_name)[0]
            entry['git_url'] = repo['git']['uri']
            entry['git_rev'] = repo['git']['version']
            entry['folder'] = pkg_name
        location_to_test = os.path.join(os.getenv('CURRENT_PATH'), '%s.patch' % pkg_name)
        if os.path.exists(location_to_test):
            entry['patches'] = [ '%s.patch' % pkg_name ]
        source.append(entry)

unsatisfied_deps = set()
outputs = []
catkin_paths = lookup.get_loader().get_catkin_paths()
for pkg_shortname in rospack.list():
    pkg_name = _resolve(pkg_shortname)[0]
    manifest = rospack.get_manifest(pkg_shortname)
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
            'host': ['python', 'setuptools', 'pip'],
            'run': ['python']
        }
    }
    pkg = catkin_pkg.package.parse_package(catkin_paths[pkg_shortname])
    pkg.evaluate_conditions(os.environ)
    deps = pkg.build_depends + pkg.buildtool_depends + pkg.run_depends + pkg.test_depends + pkg.build_export_depends + pkg.buildtool_export_depends + pkg.exec_depends
    deps = [d.name for d in deps if d.evaluated_condition]
    deps = set(deps)

    for dep in deps:
        if not _resolve(dep):
            unsatisfied_deps.add(dep)
            continue
        output['requirements']['host'].extend(_resolve(dep))
        output['requirements']['run'].extend(_resolve(dep))

    output['script'] = 'bld_.bat'
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

with open("meta.yaml", 'w') as stream:
    yaml.dump(meta, stream)
