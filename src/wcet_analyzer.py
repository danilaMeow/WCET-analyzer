import json
import sys
from dataclasses import dataclass
from typing import List, Dict, Any


@dataclass
class ProcessorModel:
    base_op_cost: int
    cache_miss_penalty: int
    branch_mispredict_penalty: int


@dataclass
class Operation:
    name: str
    op_type: str
    memory_accesses: int
    branches: int


def load_data_from_json(file_path: str) -> tuple[ProcessorModel, List[Operation], int]:
    with open(file_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    proc_data = data["processor_model"]
    processor = ProcessorModel(
        base_op_cost=proc_data["base_op_cost"],
        cache_miss_penalty=proc_data["cache_miss_penalty"],
        branch_mispredict_penalty=proc_data["branch_mispredict_penalty"]
    )
    
    operations = [
        Operation(
            name=op["name"],
            op_type=op["op_type"],
            memory_accesses=op["memory_accesses"],
            branches=op["branches"]
        )
        for op in data["operations"]
    ]
    
    deadline = data.get("deadline_cycles", 0)
    return processor, operations, deadline