import ruamel.yaml
import subprocess
import rospkg
import rosdep2
import os

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
    for tar in data:
        local_name = tar['tar']['local-name']
        pkg_name = _resolve(local_name)[0]
        entry = {}
        entry['url'] = tar['tar']['uri']
        entry['folder'] = pkg_name
        entry['fn'] = "%s.tar.gz" % pkg_name
        location_to_test = os.path.join(os.getenv('CURRENT_PATH'), '%s.patch' % pkg_name)
        if os.path.exists(location_to_test):
            entry['patches'] = [ '%s.patch' % pkg_name ]
        source.append(entry)

outputs = []
for pkg in rospack.list():
    pkg_name = _resolve(pkg)[0]
    manifest = rospack.get_manifest(pkg)
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
            'host': ['python'],
            'run': ['python']
        }
    }
    deps = lookup.get_rosdeps(pkg)
    deps = set(deps)

    for dep in deps:
        if not _resolve(dep):
            print(dep)
            continue
        output['requirements']['host'].extend(_resolve(dep))
        output['requirements']['run'].extend(_resolve(dep))

    output['script'] = 'bld_.bat'

    outputs.append(output)

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
