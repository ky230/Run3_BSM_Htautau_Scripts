#!/bin/bash

# 定义进程和年代
processes=(TTto2L2Nu TTtoLNu2Q TTto4Q)
eras=(2023)

# EOS 根目录
base_dir="/eos/cms/store/group/phys_higgs/HLepRare/skim_2025_v1"

for era in "${eras[@]}"; do
    for process in "${processes[@]}"; do
        echo "=============================="
        echo "Era: ${era}, Process: ${process}"
        
        src_dir="${base_dir}/Run3_${era}/${process}"
        if [ ! -d "$src_dir" ]; then
            echo "⚠️  路径不存在: $src_dir"
            continue
        fi
        
        # 统计文件总数
        total_files=$(ls -1 "${src_dir}"/nano_*.root 2>/dev/null | wc -l)
        if [ "$total_files" -eq 0 ]; then
            echo "⚠️  未找到 nano_*.root 文件"
            continue
        fi

        # 计算1/3文件数（向上取整）
        subset_size=$(( (total_files + 2) / 3 ))

        echo "总文件数: ${total_files}, 将处理前 ${subset_size} 个文件"

        # 循环前1/3文件并创建软链接
        for (( i=1; i<=subset_size; i++ )); do
            src="${src_dir}/nano_${i}.root"
            dst="${process}_${era}_${i}.root"
            if [ -f "$src" ]; then
                echo "链接 $src -> $dst"
                ln -sf "$src" "$dst"
            else
                echo "❌ 文件不存在: $src"
            fi
        done
    done
done
