
import abc
import json
from collections import namedtuple


#: See Editable.restrict
Restriction = namedtuple('Restriction', 'name min_value max_value min_length'
                         ' max_length validator')


class Editable(object):
    """Editable interface

    Attributes
    ----------
    keys : dict
        Mapping of restrictions

    Methods
    -------
    restrict
        Set restrictions on an attribute
    to_dict
        Generate a dict for this object
    to_json
        Generate a JSON string for this object
    """
    __metaclass__ = abc.ABCMeta

    @property
    def keys(self):
        """Map of restricted keys of this object. Keys are the names of the
        attributes. Values are Restriction instances.

        Returns
        -------
        keys : dict
        """
        try:
            return self._keys
        except AttributeError:
            self._keys = {}
            return self._keys

    def restrict(self, name, min_value=None, max_value=None, min_length=None,
                 max_length=None, validator=None):
        """Restrict an attribute. This adds the attribute to the key
        collection used to build textual representations.

        Parameters not passed will not be used to check validity.

        Parameters
        ----------
        name : string
            Name of the attribute
        min_value : optional
            Require value to be greater or equal to this value
        max_value : optional
            Require value to be less or equal to this value
        min_length : int, optional
            Require length of value to be greater or equal to this value
        max_length : int, optional
            Require length of value to be less or equal to this value
        validator : func(Editable, name, value), optional
            If set, this function gets passed the instance, name, and new
            value. This should raise a ValueError if the value should not
            be allowed.
        """
        self.keys[name] = Restriction(name, min_value, max_value, min_length,
                                      max_length, validator)

    def restrictInt8(self, name, **kwargs):
        params = {'min_value': -0x80, 'max_value': 0x7F}
        params.update(kwargs)
        self.restrict(name, **params)

    def restrictUInt8(self, name, **kwargs):
        params = {'min_value': 0, 'max_value': 0xFF}
        params.update(kwargs)
        self.restrict(name, **params)

    def restrictInt16(self, name, **kwargs):
        params = {'min_value': -0x8000, 'max_value': 0x7FFF}
        params.update(kwargs)
        self.restrict(name, **params)

    def restrictUInt16(self, name, **kwargs):
        params = {'min_value': 0, 'max_value': 0xFFFF}
        params.update(kwargs)
        self.restrict(name, **params)

    def restrictInt32(self, name, **kwargs):
        params = {'min_value': -0x80000000, 'max_value': 0x7FFFFFFF}
        params.update(kwargs)
        self.restrict(name, **params)

    def restrictUInt32(self, name, **kwargs):
        params = {'min_value': 0, 'max_value': 0xFFFFFFFF}
        params.update(kwargs)
        self.restrict(name, **params)

    def __setattr__(self, name, value):
        try:
            restriction = self.keys[name]
            restriction.name
        except:
            pass
        else:
            if restriction.min_value is not None:
                if value < restriction.min_value:
                    raise ValueError(
                        '{name}: "{value}" is less than minimum "{restrict}"'
                        .format(name=name, value=value,
                                restrict=restriction.min_value))
            if restriction.max_value is not None:
                if value > restriction.max_value:
                    raise ValueError(
                        '{name}: "{value}" is more than maximum "{restrict}"'
                        .format(name=name, value=value,
                                restrict=restriction.max_value))
            if restriction.min_length is not None:
                if len(value) < restriction.min_length:
                    raise ValueError(
                        '{name}: "{value}" is less than length "{restrict}"'
                        .format(name=name, value=value,
                                restrict=restriction.min_length))
            if restriction.max_length is not None:
                if len(value) > restriction.max_length:
                    raise ValueError(
                        '{name}: "{value}" is more than length "{restrict}"'
                        .format(name=name, value=value,
                                restrict=restriction.max_length))
            if restriction.validator is not None:
                restriction.validator(self, name, value)
        super(Editable, self).__setattr__(name, value)

    def to_dict(self):
        """Generates a dict recursively out of this instance

        Returns
        -------
        out : dict
        """
        out = {}
        for key in self.keys:
            try:
                key = key.name
            except:
                pass
            value = getattr(self, key)
            try:
                sub_out = {}
                for sub_name, sub_value in value.items():
                    try:
                        sub_out[sub_name] = sub_value.to_dict()
                    except AttributeError:
                        sub_out[sub_name] = sub_value
                out[key] = sub_out
            except (AttributeError, TypeError):
                try:
                    sub_out = []
                    for sub_value in value:
                        try:
                            sub_out.append(sub_value.to_dict())
                        except AttributeError:
                            sub_out.append(sub_value)
                    out[key] = sub_out
                except:
                    try:
                        out[key] = value.to_dict()
                    except AttributeError:
                        out[key] = value
        return out

    def to_json(self):
        """Returns the JSON version of this instance

        Returns
        -------
        json_string : string
        """
        return json.dumps(self.to_dict())
