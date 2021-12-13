from pathlib import Path
from typing import Union, List

from commitizen import git, defaults

from .base_config import BaseConfig
from .toml_config import TomlConfig
from .json_config import JsonConfig
from .yaml_config import YAMLConfig

class ConfigLoader():
    def __init__(self, path: Union[Path, str]=Path.cwd()):
        if isinstance(path, str):
            path = Path(path)
        self._path = path

    def get_config_dirs(self, customized_dir: Path) -> List[Path]:
        """Get directories where config files might be located

        Parameters
        ----------
        customized_dir : Path
            customized directory

        Returns
        -------
        List[Path]
            A list of directories
        """
        git_proj_root_dir = git.find_git_project_root()
        home_config_dir = Path.home() / '.config/'

        dirs = set({git_proj_root_dir, home_config_dir})

        if customized_dir.exists():
            dirs = [customized_dir] + list(dirs)

        return dirs

    def search_config_files(self, dirs: List[Path]) -> List[Path]:
        config_files = (
            dir / Path(fname)
            for dir in dirs
            for fname in defaults.config_files
        )

        return [file for file in config_files if file.exists()]

    def load_config(self) -> BaseConfig:
        dirs = self.get_config_dirs(self._path)
        files = self.search_config_files(dirs)

        config = BaseConfig()
        if files is None:
            return config

        for file in files:
            _config: Union[TomlConfig, JsonConfig, YAMLConfig]

            with open(file, 'rb') as f:
                data: bytes = f.read()

            if "toml" in file.suffix:
                _config = TomlConfig(data=data, path=file)
            elif "json" in file.suffix:
                _config = JsonConfig(data=data, path=file)
            elif "yaml" in file.suffix:
                _config = YAMLConfig(data=data, path=file)

            if _config.is_empty_config:
                continue
            else:
                config = _config
                break

        return config

    def __call__(self):
        return self.load_config()
