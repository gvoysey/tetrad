function [ Gain ] = Gain_Function(tetrad_1,tetrad_2)
%GAIN_FUNCTION: Calculates the 'gain' of a tetrad pair across all AML lines
%   Input: 
%   tetrad_1: <String> : Key of first tetrad as indexed in BLOODSPOT_DATA
%   tetrad_2: <String> : Key of second tetrad as indexed in BLOODSPOT_DATA

    % Load data libraries 
%     load('BLOODSPOT_DATA_formated.mat');
%     load('BLOODSPOT_DATA_unformated.mat');

    ANTIGEN_1 = Antigens_Bloodspot.(tetrad_1);
    ANTIGEN_2 = Antigens_Bloodspot.(tetrad_2);

    Healthy_Lines = {'HSC','MPP','CMP','GMP','MEP'};

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
end

