import sys

class PirateLangInterpreter:
    def __init__(self):
        self.variables = {}
        self.functions = {}
        self.loop_stack = []
    
    def interpret(self, code):
        lines = [line.strip() for line in code.split('\n') if line.strip() and not line.strip().startswith('#')]
        i = 0
        while i < len(lines):
            line = lines[i]
            i += self.execute_line(line, lines, i)
    
    def execute_line(self, line, all_lines=None, current_index=None):
        # Shout command
        if line.startswith('shout '):
            expr = line[6:].strip()
            value = self.evaluate_expression(expr)
            print(value)
            return 1
        
        # Ask command
        elif line.startswith('ask '):
            var_name = line[4:].strip()
            value = input()
            try:
                if '.' in value:
                    self.variables[var_name] = float(value)
                else:
                    self.variables[var_name] = int(value)
            except ValueError:
                self.variables[var_name] = value
            return 1
        
        # Stash command (variable assignment)
        elif ' stash ' in line:
            parts = line.split(' stash ')
            var_name = parts[0].strip()
            expr = parts[1].strip()
            value = self.evaluate_expression(expr)
            self.variables[var_name] = value
            return 1
        
        # If statement
        elif line.startswith('if '):
            condition = line[3:].strip(' {')
            if self.evaluate_condition(condition):
                block = self.get_block(all_lines, current_index)
                for block_line in block:
                    self.execute_line(block_line, all_lines, current_index)
                return len(block) + 1
            else:
                block = self.get_block(all_lines, current_index)
                return len(block) + 1
        
        # Loop command
        elif line.startswith('loop '):
            condition = line[5:].strip(' {')
            if condition.startswith('if '):
                condition = condition[3:].strip()
            block = self.get_block(all_lines, current_index)
            while self.evaluate_condition(condition):
                for block_line in block:
                    self.execute_line(block_line, all_lines, current_index)
            return len(block) + 1
        
        # Function declaration
        elif line.startswith('plunder '):
            func_name = line[8:].split('(')[0].strip()
            self.functions[func_name] = {
                'start': current_index,
                'end': self.find_block_end(all_lines, current_index)
            }
            return self.functions[func_name]['end'] - current_index + 1
        
        # Return statement
        elif line.startswith('booty '):
            expr = line[6:].strip()
            return self.evaluate_expression(expr)
        
        # Function call
        elif '(' in line and ')' in line and not line.startswith('if ') and not line.startswith('loop '):
            func_name = line.split('(')[0].strip()
            if func_name in self.functions:
                start = self.functions[func_name]['start'] + 1
                end = self.functions[func_name]['end']
                for i in range(start, end):
                    self.execute_line(all_lines[i], all_lines, i)
                return 1
        
        return 1
    
    def evaluate_expression(self, expr):
        # Property access: like original.length
        if '.' in expr:
            var_part, prop_part = expr.split('.', 1)
            var_part = var_part.strip()
            prop_part = prop_part.strip()
            if var_part in self.variables:
                val = self.variables[var_part]
                if prop_part == 'length':
                    return len(val)
        
        # Check if it's a variable
        if expr in self.variables:
            return self.variables[expr]
        
        # String literal
        if expr.startswith('"') and expr.endswith('"'):
            return expr[1:-1]
        
        # Number
        if expr.replace('.', '', 1).isdigit():
            return float(expr) if '.' in expr else int(expr)
        
        # Boolean values
        if expr == 'aye':
            return True
        if expr == 'nay':
            return False
        
        # Array or string access like original[i]
        if '[' in expr and ']' in expr:
            var_name = expr.split('[')[0].strip()
            index_expr = expr.split('[')[1].split(']')[0].strip()
            index = self.evaluate_expression(index_expr)
            if var_name in self.variables and isinstance(self.variables[var_name], (str, list)):
                return self.variables[var_name][index]
        
        # Arithmetic operations
        ops = ['+', '-', '*', '/']
        for op in ops:
            if op in expr:
                parts = expr.split(op, 1)
                left = self.evaluate_expression(parts[0].strip())
                right = self.evaluate_expression(parts[1].strip())
                if op == '+':
                    if isinstance(left, str) or isinstance(right, str):
                        return str(left) + str(right)
                    return left + right
                elif op == '-':
                    return left - right
                elif op == '*':
                    if isinstance(left, (int, float)) and isinstance(right, (int, float)):
                        return left * right
                    raise TypeError("Can only multiply numbers, matey!")
                elif op == '/':
                    return left / right
        
        return expr
    
    def evaluate_condition(self, condition):
        if ' be ' in condition:
            parts = condition.split(' be ')
            left = self.evaluate_expression(parts[0].strip())
            right = self.evaluate_expression(parts[1].strip())
            return left == right
        
        comparisons = [' <= ', ' >= ', ' < ', ' > ']
        for comp in comparisons:
            if comp in condition:
                parts = condition.split(comp)
                left = self.evaluate_expression(parts[0].strip())
                right = self.evaluate_expression(parts[1].strip())
                
                if isinstance(left, str) and right not in self.variables:
                    try:
                        left = float(left) if '.' in left else int(left)
                    except ValueError:
                        pass
                if isinstance(right, str) and right not in self.variables:
                    try:
                        right = float(right) if '.' in right else int(right)
                    except ValueError:
                        pass
                
                if comp == ' < ':
                    return left < right
                elif comp == ' > ':
                    return left > right
                elif comp == ' <= ':
                    return left <= right
                elif comp == ' >= ':
                    return left >= right
        
        if condition == 'aye':
            return True
        if condition == 'nay':
            return False
        
        return bool(self.evaluate_expression(condition))
    
    def get_block(self, all_lines, start_index):
        block = []
        i = start_index + 1
        indent = 0
        
        while i < len(all_lines):
            line = all_lines[i]
            if line.endswith('{'):
                indent += 1
            if line.startswith('}'):
                if indent == 0:
                    break
                indent -= 1
            if indent == 0 and not line.startswith('}'):
                block.append(line)
            elif indent > 0 or line.endswith('{'):
                block.append(line)
            i += 1
        
        return block
    
    def find_block_end(self, all_lines, start_index):
        i = start_index + 1
        indent = 0
        while i < len(all_lines):
            line = all_lines[i]
            if line.endswith('{'):
                indent += 1
            if line.startswith('}'):
                if indent == 0:
                    return i
                indent -= 1
            i += 1
        return len(all_lines) - 1

def main():
    if len(sys.argv) < 2:
        print("Usage: python piratelang.py programs/<filename>")
        sys.exit(1)
    
    filename = sys.argv[1]
    with open(filename, 'r') as file:
        code = file.read()
    
    interpreter = PirateLangInterpreter()
    interpreter.interpret(code)

if __name__ == "__main__":
    main()