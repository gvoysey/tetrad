%% BE 561: Final Project
%  Antigen Tetrad-Set Selection 
%  BloodSpot Data Formater

%% Init Settings 
clear all;
close all; 
set(groot, ...
    'DefaultAxesLineWidth', 1,          ...
    'DefaultAxesXColor', 'k',           ...
    'DefaultAxesYColor', 'k',           ...
    'DefaultAxesFontUnits', 'points',   ...
    'DefaultAxesFontSize', 16,          ...
    'DefaultAxesFontName', 'Helvetica', ...
    'DefaultLineLineWidth', 1,          ...
    'DefaultTextFontUnits', 'Points',   ...
    'DefaultTextFontSize', 20,          ...
    'DefaultTextFontName', 'Helvetica', ...
    'DefaultAxesBox', 'off'  );
set(groot, 'DefaultAxesTickDir', 'in');
set(groot, 'DefaultAxesTickDirMode', 'auto');


%% Load Resources & Structure Data 

Healthy_Lines = {'HSC','MPP','CMP','GMP','MEP'};
Antigens_Bloodspot  = struct; 
Antigen_Dictionary  = {};
CellLine_Dictionary = {};
DataSets            = {'C:\Users\Kestas\Documents\MATLAB\Antigen Project\bloodspot'};
Antigen_Index       = 0;

for DataFile = 1:length(DataSets)
    
    cd( DataSets{DataFile} );
    directory = dir;
    
    for Data = 1:length(directory) 
        
        filename = directory(Data).name;
        [path,name,ext] = fileparts(filename);
        
        if( ~strcmp(ext,'.mat') )
            continue;
        end
        
        Antigen_Index = Antigen_Index + 1; 
                
        temp            = load(filename);
        field           = fieldnames(temp);
        field           = field{1};
        name = strrep(name,"_log2",[]);
        Antigens_Bloodspot.(name) = struct;
        Antigens_Bloodspot.(name) = temp.(field);
    end
end

Antigen_Dictionary  = fields(Antigens_Bloodspot);
temp                = Antigen_Dictionary{1};
tempLine            = Antigens_Bloodspot.(temp);
CellLine_Dictionary = fields(tempLine);

Num_Antigens  = numel(Antigen_Dictionary);
Num_CellLines = numel(CellLine_Dictionary);


%% Step 1.0: Normalization & Mean+Std Layering

for antigen = 1:Num_Antigens
   
    for cellLine = 1:Num_CellLines
      temp_ant  = Antigens_Bloodspot.(Antigen_Dictionary{antigen});
      temp_cell = temp_ant.(CellLine_Dictionary{cellLine});
      
      Antigens_Bloodspot.(Antigen_Dictionary{antigen}).(CellLine_Dictionary{cellLine}) = struct; 
      
      Antigens_Bloodspot.(Antigen_Dictionary{antigen}).(CellLine_Dictionary{cellLine}).data = temp_cell;
      Antigens_Bloodspot.(Antigen_Dictionary{antigen}).(CellLine_Dictionary{cellLine}).mean = mean(temp_cell);
      Antigens_Bloodspot.(Antigen_Dictionary{antigen}).(CellLine_Dictionary{cellLine}).std  = std(temp_cell);
      Antigens_Bloodspot.(Antigen_Dictionary{antigen}).(CellLine_Dictionary{cellLine}).num  = length(temp_cell);
    end
    
end

for antigen = 1:Num_Antigens
    mean_vector = zeros(1,length(Healthy_Lines));
    for cellLine = 1:Num_CellLines
        if ( ismember((CellLine_Dictionary{cellLine}),Healthy_Lines) )
            mean_vector(cellLine) = Antigens_Bloodspot.(Antigen_Dictionary{antigen}).(CellLine_Dictionary{cellLine}).mean;
        end
    end
    meanOfmeans =  mean(mean_vector);
    for cellLine = 1:Num_CellLines
        if (~ ismember((CellLine_Dictionary{cellLine}),Healthy_Lines) )
            Antigens_Bloodspot.(Antigen_Dictionary{antigen}).(CellLine_Dictionary{cellLine}).normalized = Antigens_Bloodspot.(Antigen_Dictionary{antigen}).(CellLine_Dictionary{cellLine}).data ./ meanOfmeans;
        end
    end
end


save('BLOODSPOT_DATA_unformated','Antigen_Dictionary','CellLine_Dictionary')
save('BLOODSPOT_DATA_formated','Antigens_Bloodspot');



