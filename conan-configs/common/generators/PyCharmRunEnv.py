from pathlib import Path
from typing import Dict

from conans import tools
from conans.model import Generator
from jinja2 import Template
from conan.tools.env.virtualrunenv import VirtualRunEnv

class PyCharmRunEnv(Generator):
    @property
    def _base_dir(self):
        return Path("$PROJECT_DIR$", "venv")

    @property
    def _py_interp(self):
        if self.settings.os == "Windows":
            py_interp = Path(*[f'"{p}"' if " " in p else p for p in self._base_dir.joinpath("Scripts", "python.exe").parts])
            return py_interp
        return self._base_dir.joinpath("bin", "python")

    @property
    def _site_packages(self):
        if self.settings.os == "Windows":
            return self._base_dir.joinpath("Lib", "site-packages")
        py_version = tools.Version(self.conanfile.deps_cpp_info["cpython"].version)
        return self._base_dir.joinpath("lib", f"python{py_version.major}.{py_version.minor}", "site-packages")

    @property
    def filename(self):
        pass

    @property
    def content(self) -> Dict[str, str]:
        # Mapping of file names -> files
        run_configurations: Dict[str, str] = {}

        if not hasattr(self.conanfile, "_pycharm_targets"):
            # There are no _pycharm_targets in the conanfile for the package using this generator.
            return run_configurations

        # Collect environment variables for use in the template
        env = VirtualRunEnv(self.conanfile).environment()
        env.prepend_path("PYTHONPATH", str(self._site_packages))

        if hasattr(self.conanfile, f"_{self.conanfile.name}_run_env"):
            project_run_env = getattr(self.conanfile, f"_{self.conanfile.name}_run_env")
            if project_run_env:
                env.compose_env(project_run_env)  # TODO: Add logic for dependencies

        # Create Pycharm run configuration from template for each target
        for target in self.conanfile._pycharm_targets:
            target["env_vars"] = env.vars(self.conanfile, scope="run")
            target["sdk_path"] = str(self._py_interp)
            if "parameters" not in target:
                target["parameters"] = ""

            with open(target["jinja_path"], "r") as f:
                template = Template(f.read())
                run_configuration = template.render(target)
                run_configurations[str(Path(self.conanfile.source_folder).joinpath(".run", f"{target['name']}.run.xml"))] = run_configuration

        return run_configurations
