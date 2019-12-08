from typing import Any, NamedTuple, List, Type, Tuple
import inspect


def pick_class_mame(items: List[Any], pick_first: bool = False, pick_last: bool = True) -> str:
    if len(items) < 1:
        raise ValueError(dict(message='cannot choose from empty list'))
    if pick_first == pick_last:
        raise ValueError(dict(message='cannot pick both first and last', pick_first=pick_first, pick_last=pick_last))
    index = [0, -1][pick_last and not pick_first]
    return items[index].__class__.__name__


def combine_named_tuples(*named_tuples: Tuple[NamedTuple], class_name: str = None, handle_methods: bool = False,
                         pick_first: bool = False, pick_last: bool = True) -> NamedTuple:
    class_name = class_name or pick_class_mame(named_tuples, pick_first=pick_first, pick_last=pick_last)
    # TODO: enforce tuples have mutually exclusive fields
    field_types = [field_type for named_tuple in named_tuples for field_type in named_tuple._field_types.items()]
    field_data = {key: val for named_tuple in named_tuples for key, val in named_tuple._asdict().items()}
    output_type: Type[NamedTuple] = NamedTuple(typename=class_name, fields=field_types)

    if handle_methods:
        for named_tuple in named_tuples:
            field_names = set(named_tuple._fields)
            for name, member in inspect.getmembers(named_tuple.__class__):
                if name.startswith('_') or name in field_names:
                    continue
                if inspect.isfunction(member) or inspect.isdatadescriptor(member):
                    setattr(output_type, name, member)

    instance = output_type(**field_data)
    return instance
