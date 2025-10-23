mkdir -p Logs  # 确保 Logs 目录存在

for era in 2022EE 2022postEE 2023preBPix 2023postBPix ; do
    for channel in et mt tt em None ; do
        echo "Submitting btag-eff for era=$era, channel=$channel"
        python3 btag-eff_dxc.py Skimmed_sample/${era}/TTto*.root $era $channel \
            > Logs/${era}_${channel}_withDeltaR.log 2>&1 &
    done
    wait  # 等待当前 era 的所有 channel 作业完成后再进行下一个 era
done

echo "All jobs submitted and completed era by era. Check Logs/ for output."
# 
