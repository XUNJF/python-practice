import ast
import operator


_OPS = {
    ast.Add: operator.add,
    ast.Sub: operator.sub,
    ast.Mult: operator.mul,
    ast.Div: operator.truediv,
    ast.Pow: operator.pow,
    ast.mod: operator.mod,
    ast.USub: operator.neg,
    ast.UAdd: operator.pos,
}

def safe_eval(expr):
    def walk(node):
        if isinstance(node, ast.Constant) and isinstance(node.value, (int, float)):
            return node.value
        if isinstance(node, ast.BinOp) and type(node.op) in _OPS:
            return _OPS[type(node.op)](walk(node.left), walk(node.right))
        if isinstance(node, ast.UnaryOp) and type(node.op) in _OPS:
            return _OPS[type(node.op)](walk(node.operand))
        raise ValueError(f"不支持的写法：{type(node).__name__}")
    return walk(ast.parse(expr, mode="eval").body)


if __name__ == "__main__":
    print("=== 正常算式 ===") 
    for e in ["8472+3951", "(8472+3951)*27-1364", "847.36*29.7", "2**47", "-5+3"]:
        print(f"    {e:<22} = {safe_eval(e)}")

    print()
    print("=== 危险输入（必须被挡住）===")
    for e in [
        "__import__('os').system('echo 哈哈')",                                                                                                                                                                                                                                                                                                                                                                            
        "open('/etc/passwd').read()",
        "[1,2,3]",
        "1 if True else 2",
    ]:
        try:
            print(f"  ✗✗ {e}  ->  {safe_eval(e)}")
        except Exception as ex:
            print(f"  ✓ 挡住 {e[:34]:<36} {type(ex).__name__}")