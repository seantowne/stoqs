# Generated by the protocol buffer compiler.  DO NOT EDIT!

from google.protobuf import descriptor
from google.protobuf import message
from google.protobuf import reflection
from google.protobuf import descriptor_pb2
# @@protoc_insertion_point(imports)



DESCRIPTOR = descriptor.FileDescriptor(
  name='trex.proto',
  package='org.mbari.trex',
  serialized_pb='\n\ntrex.proto\x12\x0eorg.mbari.trex\"\x92\x02\n\tPredicate\x12\x0e\n\x06object\x18\x01 \x02(\t\x12\x11\n\tpredicate\x18\x02 \x02(\t\x12\r\n\x05start\x18\x03 \x02(\x06\x12\x36\n\nattributes\x18\x04 \x03(\x0b\x32\".org.mbari.trex.Predicate.Variable\x1a+\n\x0b\x46loatDomain\x12\r\n\x05min_v\x18\x01 \x01(\x01\x12\r\n\x05max_v\x18\x02 \x01(\x01\x1an\n\x08Variable\x12\x0c\n\x04name\x18\x01 \x02(\t\x12\x34\n\x05int_d\x18\x02 \x01(\x0b\x32%.org.mbari.trex.Predicate.FloatDomain\x12\x0e\n\x06\x62ool_d\x18\x03 \x01(\x08\x12\x0e\n\x06\x65num_d\x18\x04 \x03(\t')




_PREDICATE_FLOATDOMAIN = descriptor.Descriptor(
  name='FloatDomain',
  full_name='org.mbari.trex.Predicate.FloatDomain',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  fields=[
    descriptor.FieldDescriptor(
      name='min_v', full_name='org.mbari.trex.Predicate.FloatDomain.min_v', index=0,
      number=1, type=1, cpp_type=5, label=1,
      has_default_value=False, default_value=0,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    descriptor.FieldDescriptor(
      name='max_v', full_name='org.mbari.trex.Predicate.FloatDomain.max_v', index=1,
      number=2, type=1, cpp_type=5, label=1,
      has_default_value=False, default_value=0,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
  ],
  extensions=[
  ],
  nested_types=[],
  enum_types=[
  ],
  options=None,
  is_extendable=False,
  extension_ranges=[],
  serialized_start=150,
  serialized_end=193,
)

_PREDICATE_VARIABLE = descriptor.Descriptor(
  name='Variable',
  full_name='org.mbari.trex.Predicate.Variable',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  fields=[
    descriptor.FieldDescriptor(
      name='name', full_name='org.mbari.trex.Predicate.Variable.name', index=0,
      number=1, type=9, cpp_type=9, label=2,
      has_default_value=False, default_value=str("", "utf-8"),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    descriptor.FieldDescriptor(
      name='int_d', full_name='org.mbari.trex.Predicate.Variable.int_d', index=1,
      number=2, type=11, cpp_type=10, label=1,
      has_default_value=False, default_value=None,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    descriptor.FieldDescriptor(
      name='bool_d', full_name='org.mbari.trex.Predicate.Variable.bool_d', index=2,
      number=3, type=8, cpp_type=7, label=1,
      has_default_value=False, default_value=False,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    descriptor.FieldDescriptor(
      name='enum_d', full_name='org.mbari.trex.Predicate.Variable.enum_d', index=3,
      number=4, type=9, cpp_type=9, label=3,
      has_default_value=False, default_value=[],
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
  ],
  extensions=[
  ],
  nested_types=[],
  enum_types=[
  ],
  options=None,
  is_extendable=False,
  extension_ranges=[],
  serialized_start=195,
  serialized_end=305,
)

_PREDICATE = descriptor.Descriptor(
  name='Predicate',
  full_name='org.mbari.trex.Predicate',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  fields=[
    descriptor.FieldDescriptor(
      name='object', full_name='org.mbari.trex.Predicate.object', index=0,
      number=1, type=9, cpp_type=9, label=2,
      has_default_value=False, default_value=str("", "utf-8"),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    descriptor.FieldDescriptor(
      name='predicate', full_name='org.mbari.trex.Predicate.predicate', index=1,
      number=2, type=9, cpp_type=9, label=2,
      has_default_value=False, default_value=str("", "utf-8"),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    descriptor.FieldDescriptor(
      name='start', full_name='org.mbari.trex.Predicate.start', index=2,
      number=3, type=6, cpp_type=4, label=2,
      has_default_value=False, default_value=0,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    descriptor.FieldDescriptor(
      name='attributes', full_name='org.mbari.trex.Predicate.attributes', index=3,
      number=4, type=11, cpp_type=10, label=3,
      has_default_value=False, default_value=[],
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
  ],
  extensions=[
  ],
  nested_types=[_PREDICATE_FLOATDOMAIN, _PREDICATE_VARIABLE, ],
  enum_types=[
  ],
  options=None,
  is_extendable=False,
  extension_ranges=[],
  serialized_start=31,
  serialized_end=305,
)

_PREDICATE_FLOATDOMAIN.containing_type = _PREDICATE;
_PREDICATE_VARIABLE.fields_by_name['int_d'].message_type = _PREDICATE_FLOATDOMAIN
_PREDICATE_VARIABLE.containing_type = _PREDICATE;
_PREDICATE.fields_by_name['attributes'].message_type = _PREDICATE_VARIABLE
DESCRIPTOR.message_types_by_name['Predicate'] = _PREDICATE

class Predicate(message.Message, metaclass=reflection.GeneratedProtocolMessageType):
  class FloatDomain(message.Message, metaclass=reflection.GeneratedProtocolMessageType):
    DESCRIPTOR = _PREDICATE_FLOATDOMAIN
    
    # @@protoc_insertion_point(class_scope:org.mbari.trex.Predicate.FloatDomain)
  
  class Variable(message.Message, metaclass=reflection.GeneratedProtocolMessageType):
    DESCRIPTOR = _PREDICATE_VARIABLE
    
    # @@protoc_insertion_point(class_scope:org.mbari.trex.Predicate.Variable)
  DESCRIPTOR = _PREDICATE
  
  # @@protoc_insertion_point(class_scope:org.mbari.trex.Predicate)

# @@protoc_insertion_point(module_scope)
