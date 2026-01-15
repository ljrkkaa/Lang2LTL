import subprocess

# LTL 公式
# ltl_formula = "<> ( repairp3 && ! scanp3 && <> scanp3 ) && <> ( washp21 && <> mowp21 && <> scanp21 ) && <> ( sweepp21 && ! washp21 && <> mowp21 ) && <> ( fixt5 && ! p18 ) && ! p24 U sweepp27 && <> ( washp34 && X scanp34 )"

ltl_formula = "<> ( repairp3 && ! scanp3 && <> scanp3 ) && <> ( washp21 && <> mowp21 && <> scanp21 ) && <> ( sweepp21 && ! washp21 && <> mowp21 )"

# 输出文件
output_file = "nba_output.txt"

# 调用 ltl2ba 并将结果写入文件
with open(output_file, "w") as f:
    subprocess.run(
        ["./ltl2ba-1.3/ltl2ba", "-s", "-f", ltl_formula],
        stdout=f,  # 标准输出重定向到文件
        stderr=subprocess.PIPE,  # 错误输出捕获，可打印或记录
        text=True,
    )

print(f"NBA 输出已保存到 {output_file}")
