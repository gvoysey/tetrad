%% BE 561: Final Project
%  Antigen Tetrad-Set Selection
%  Gain Annotattion
%  Last modified: Dec 6 2017 Kestutis S.
clear all
close all

load('BLOODSPOT_DATA_formated.mat');
load('BLOODSPOT_DATA_unformated.mat');
tetrads = importfile('full_tree_tetrads.csv');
Healthy_Lines = {'HSC','MPP','CMP','GMP','MEP'};

for i = 2:height(tetrads)

    tetrad = tetrads{i,'VarName1'};
    pairs  = strsplit(tetrad,',');
    Gain_Vec = zeros(1,4);
    for j = 1:4
       
        tetrad_1 = pairs{j*2-1};
        tetrad_2 = pairs{j*2};
        ANTIGEN_1 = Antigens_Bloodspot.(tetrad_1);
        ANTIGEN_2 = Antigens_Bloodspot.(tetrad_2);

        gain_vec = zeros( 1,length(CellLine_Dictionary) - length(Healthy_Lines) );
        
        cellCount = 0;
        for cellLine = 1:length(CellLine_Dictionary)
            if ( ismember((CellLine_Dictionary{cellLine}),Healthy_Lines) )
                continue;
            end
            cellCount = cellCount + 1;
            gain_vec(cellCount) = min( ANTIGEN_1.(CellLine_Dictionary{cellLine}).normalized_mean_log10 , ANTIGEN_2.(CellLine_Dictionary{cellLine}).normalized_mean_log10 );
        end
        
        Gain = sum(gain_vec);
        Gain_Vec(j)  = Gain;
    end
    tetrads{i,'gain'} = sum(Gain_Vec);
end

writetable(tetrads,'tetrads_assesed2.csv','Delimiter',',','QuoteStrings',true)
type 'tetrads_assesed2.csv'
