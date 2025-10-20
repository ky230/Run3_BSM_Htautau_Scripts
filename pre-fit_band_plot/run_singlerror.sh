


# source ../hush.sh

#source /data/pku/home/LeyanLee13/Htautau/Version12_sample_post-processing/init.sh 


var="jesUncBBEC1"
  
for channel in 'mt'   'em' 'tt' 'et'  ;  do  #  em tt 'mt'   'mt'   'em' 'mt' 'et'    'mt' et  em
for year in     "2022postEE"   "2022EE" "2023" "2023BPix"; do  #   2022EE    "2022postEE"   "2022EE" "2023" "2023BPix"


mkdir -p PNGs_${var}_V12




# rm -r PNGs_${var}_V12/${year}_${channel}_${var}_V12
#python3 plot_config_prefit_single_error_up_down.py V12/${year}_${channel}_Version12_PNN_allsyst PNGs_${var}_V12/${year}_${channel}_${var}_V12  > /data/pku/home/LeyanLee13/Htautau/Plotting_2025/Scripts/V12/Logs/${year}_${channel}_V12_${var}.log 2>&1 &
python3 plot_config_prefit_single_error_up_down.py V12/${year}_${channel}_Version12_PNN_allsyst PNGs_${var}_V12/${year}_${channel}_${var}_V12_signal --PNN  > /data/pku/home/LeyanLee13/Htautau/Plotting_2025/Scripts/V12/Logs/${year}_${channel}_V12_${var}.log 2>&1 &

done 
done
