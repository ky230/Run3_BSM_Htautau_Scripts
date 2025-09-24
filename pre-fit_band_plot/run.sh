


# source ../hush.sh



  
for channel in em et tt mt  ;  do  #  em tt 'mt'   'mt'   'em' 'mt' 'et'    'mt' et  em
for year in     2022EE 2022postEE  2023BPix 2023; do  #   2022EE    "2022EE"   "2022EE" 2023 2023BPix


mkdir -p PNGs_statonly_V12

mkdir -p PNGs_fullsyst_V12


#  PNN input var 
rm -r PNGs_fullsyst_V12/${year}_${channel}_fullsyst_V12
python3 plot_config_prefit_equal_band.py V12/${year}_${channel}_Version12_PNN_allsyst PNGs_fullsyst_V12/${year}_${channel}_fullsyst_V12  > /data/pku/home/LeyanLee13/Htautau/Plotting_2025/Scripts/V12/Logs/${year}_${channel}_V12_fullsyst.log 2>&1 &

rm -r PNGs_statonly_V12/${year}_${channel}_statonly_V12
python3 plot_config_prefit_equal_band.py V12/${year}_${channel}_Version12_PNN_allsyst PNGs_statonly_V12/${year}_${channel}_statonly_V12 --statonly   > /data/pku/home/LeyanLee13/Htautau/Plotting_2025/Scripts/V12/Logs/${year}_${channel}_V12_statonly.log 2>&1 &


# PNN score


python3 plot_config_prefit_equal_band.py V12/${year}_${channel}_Version12_PNN_allsyst PNGs_fullsyst_V12/${year}_${channel}_fullsyst_V12 -PNN > /data/pku/home/LeyanLee13/Htautau/Plotting_2025/Scripts/V12/Logs/${year}_${channel}_V12_fullsyst.log 2>&1 &


python3 plot_config_prefit_equal_band.py V12/${year}_${channel}_Version12_PNN_allsyst PNGs_statonly_V12/${year}_${channel}_statonly_V12 --statonly -PNN   > /data/pku/home/LeyanLee13/Htautau/Plotting_2025/Scripts/V12/Logs/${year}_${channel}_V12_statonly.log 2>&1 &

done 
done