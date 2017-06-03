from configparser import ConfigParser


def file_to_list(name):
    with open(name, 'r') as file:
        strs = file.readlines()
        strs = [mystr.replace('\n', '').replace('\r', '') for mystr in strs]
    return strs


class ConfigReader(ConfigParser):
    cfg = {}
    types_params = {}

    def __init__(self, *args, **kwargs):
        super(ConfigReader, self).__init__(*args, **kwargs)

    def config_read(self, filename):
        """
        Read from config file to dict in format: {"section: {parameter: value}}
        """
        self.read(filename)
        # Read all sections from config
        for section in self.sections():
            for key in self.options(section):
                self.cfg[key] = self.get(section, key)
        if not self.types_params:
            return self.cfg
        else:
            return self.check_and_set_config()

    def check_and_set_config(self):
        """
        Checking a dict config that corresponds to their types.
        After, creating the new dict config with valid types variables python.

        Arguments:
            config dict in format is {parameter: value}
            dict of typesParams in format is {parameter: 'type variable'}
            variable can pass follows type: 'bool', 'int', and 'str'
        """
        myconfig = {}
        if not self.types_params:
            raise KeyError("Attribute 'types_params' don't set!")
        try:
            for key, value in self.types_params.items():
                if value == 'bool':
                    myconfig[key] = bool(int(self.cfg[key]))
                elif value == 'int':
                    myconfig[key] = int(self.cfg[key])
                else:
                    myconfig[key] = self.cfg[key]
        except ValueError:
            raise ValueError("Parameter '{0}' set wrong in config.ini"
                             .format(key))
        except KeyError:
            raise KeyError("Parameter '{0}' don't set in config.ini"
                           .format(key))
        else:
            return myconfig
