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

def best_case(op: Operation, model: ProcessorModel) -> int:
    return model.base_op_cost

def worst_case(op: Operation, model: ProcessorModel) -> int:
    memory_penalty = op.memory_accesses * model.cache_miss_penalty
    branch_penalty = op.branches * model.branch_mispredict_penalty
    return model.base_op_cost + memory_penalty + branch_penalty

def bcet(fragment: List[Operation], model: ProcessorModel) -> int:
    return sum(best_case(op, model) for op in fragment)

def wcet(fragment: List[Operation], model: ProcessorModel) -> int:
    return sum(worst_case(op, model) for op in fragment)

def nondeterminism_ratio(fragment: List[Operation], model: ProcessorModel) -> float:
    b = bcet(fragment, model)
    return wcet(fragment, model) / b if b != 0 else 0.0

def source_breakdown(fragment: List[Operation], model: ProcessorModel) -> Dict[str, int]:
    mem_penalty = sum(op.memory_accesses * model.cache_miss_penalty for op in fragment)
    branch_penalty = sum(op.branches * model.branch_mispredict_penalty for op in fragment)
    base_cost = sum(model.base_op_cost for op in fragment)
    return {
        "base_cost": base_cost,
        "memory_penalty": mem_penalty,
        "branch_penalty": branch_penalty
    }

def main():
    file_path = "data/variant_coding.json" if len(sys.argv) < 2 else sys.argv[1]
    processor, fragment, deadline = load_data_from_json(file_path)

    print("=" * 70)
    print(" АНАЛИЗ ВРЕМЕНИ ВЫПОЛНЕНИЯ (WCET / BCET)")
    print(" Вариант: Кодирование сообщения помехоустойчивым кодом")
    print("=" * 70)
    
    print(f"\n{'Операция':<25} | {'Тип':<15} | {'BCET (такты)':<12} | {'WCET (такты)':<12}")
    print("-" * 70)
    for op in fragment:
        b = best_case(op, processor)
        w = worst_case(op, processor)
        print(f"{op.name:<25} | {op.op_type:<15} | {b:<12} | {w:<12}")
    print("-" * 70)

    total_bcet = bcet(fragment, processor)
    total_wcet = wcet(fragment, processor)
    ratio = nondeterminism_ratio(fragment, processor)
    breakdown = source_breakdown(fragment, processor)

    print(f"\nИТОГОВЫЕ РЕЗУЛЬТАТЫ:")
    print(f"  • BCET (Лучшее время):             {total_bcet} тактов")
    print(f"  • WCET (Наихудшее время):          {total_wcet} тактов")
    print(f"  • Коэффициент недетерминизма:       {ratio:.2f}")
    print(f"  • Вклад базовых операций:           {breakdown['base_cost']} тактов")
    print(f"  • Вклад задержек памяти (кэш):     {breakdown['memory_penalty']} тактов")
    print(f"  • Вклад ошибок ветвления:          {breakdown['branch_penalty']} тактов")
    print("-" * 70)

    if deadline > 0:
        print(f"Проверка дедлайна ({deadline} тактов):")
        if total_wcet <= deadline:
            print("  [УСПЕХ] Фрагмент гарантированно укладывается в дедлайн в наихудшем случае.")
        else:
            print("  [ОШИБКА] Фрагмент НЕ укладывается в дедлайн в наихудшем случае!")
    print("=" * 70)


if __name__ == "__main__":
    main()