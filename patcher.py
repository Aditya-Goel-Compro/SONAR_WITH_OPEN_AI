def apply_fix(file_path, fixed_code, start_line, end_line):

    try:
        with open(file_path, "r", encoding="utf-8") as f:
            lines = f.readlines()

        fixed_lines = fixed_code.splitlines(keepends=True)

        start_idx = start_line - 1
        end_idx = end_line

        new_lines = lines[:start_idx] + fixed_lines + lines[end_idx:]

        with open(file_path, "w", encoding="utf-8") as f:
            f.writelines(new_lines)

        print(f"✅ Fix applied: {file_path} ({start_line}-{end_line})")

    except Exception as e:
        print("❌ Patch error:", e)