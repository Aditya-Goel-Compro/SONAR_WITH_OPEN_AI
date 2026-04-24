def apply_fix(file_path, fixed_code, start_line, end_line):

    try:
        with open(file_path, "r", encoding="utf-8") as f:
            lines = f.readlines()

        # 🔥 Only modify ONE line (start_line)
        target_index = start_line - 1

        if target_index < 0 or target_index >= len(lines):
            print("❌ Invalid line index")
            return

        # Take only first line from AI output
        fixed_lines = fixed_code.strip().splitlines()

        if not fixed_lines:
            print("⚠ Empty fix, skipping")
            return

        new_line = fixed_lines[0] + "\n"

        print("\n🔧 BEFORE:")
        print(lines[target_index])

        print("🔧 AFTER:")
        print(new_line)

        # ✅ Replace ONLY that line
        lines[target_index] = new_line

        with open(file_path, "w", encoding="utf-8") as f:
            f.writelines(lines)

        print(f"✅ Fix applied safely: {file_path} (line {start_line})")

    except Exception as e:
        print("❌ Patch error:", e)