# Copyright 2022 Avaiga Private Limited
#
# Licensed under the Apache License, Version 2.0 (the "License"); you may not use this file except in compliance with
# the License. You may obtain a copy of the License at
#
#        http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on
# an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the
# specific language governing permissions and limitations under the License.

from abc import ABC
import typing as t
import warnings

from ..types import _AttributeType
from .utils import _to_camel_case
from .builder import _Builder

if t.TYPE_CHECKING:
    from ..gui import Gui


class UserAttribute(ABC):

    def __init__(self, name: str, attribute_type: _AttributeType, default_value: t.Optional[t.Any], js_name: t.Optional[str] = None) -> None:
        self.name = name
        self.attribute_type = attribute_type
        self.default_value = default_value
        self.js_name = js_name
        super().__init__()
    
    def get_js_name(self) -> str:
        return self.js_name or _to_camel_case(self.name)

    def check(self, control: str):
        if not isinstance(self.name, str) or not self.name or not self.name.isidentifier():
            warnings.warn(f"User Control '{control}' should have a valid attribute name '{self.name}'")
        if not isinstance(self.attribute_type, _AttributeType):
            warnings.warn(f"User Attribute '{control}.{self.name}' should have a valid type '{self.attribute_type}'")
    
    def get_tuple(self) -> tuple:
        return (self.name, self.attribute_type, self.default_value)


class UserControl(ABC):
    
    def __init__(self, name: str, default_attribute: str, attributes: t.List[UserAttribute], js_name: t.Optional[str] = None) -> None:
        self.name = name
        self.default_attribute = default_attribute
        self.attributes = attributes
        self.js_name = js_name
        super().__init__()

    def get_js_name(self) -> str:
        return self.js_name or _to_camel_case(self.name)

    def check(self):
        if not isinstance(self.name, str) or not self.name or not self.name.isidentifier():
            warnings.warn(f"User Control should have a valid name '{self.name}'")
        default_found = False
        for attr in self.attributes:
            if isinstance(attr, UserAttribute):
                attr.check(self.name)
                if not default_found:
                    default_found = self.default_attribute == attr.name
            else:
                warnings.warn(f"User Attribute should inherit from 'BaseAttribute' '{self.name}.{attr}'")
        if not default_found:
            warnings.warn(f"User Default Attribute should be describe in the 'attributes' List '{self.name}{self.default_attribute}'")
    
    def call_builder(self, gui: "Gui", all_properties: t.Optional[t.Dict[str, t.Any]]):
        default_attr: t.Optional[UserAttribute] = None
        attrs = []
        for ua in self.attributes:
            if self.default_attribute == ua.name:
                default_attr = ua
            else:
                attrs.append(ua.get_tuple())
        build = _Builder(
            gui=gui,
            control_type=self.name,
            element_name=self.get_js_name(),
            attributes=all_properties,
        )
        if default_attr is not None:
            build.set_value_and_default(var_name=default_attr.name, var_type = default_attr.attribute_type, default_val=default_attr.default_value)
        return build.set_attributes(attrs)
