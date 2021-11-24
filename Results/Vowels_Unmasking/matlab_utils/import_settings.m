function [dataDir, options, c, d] = import_settings()


dataDir = Cloudstation('Vowels\Spatial_Unmasking\Cooling\Vowels\Cross-referenced Behavior');

options = struct('coolThreshold',   11,...
                 'warmThreshold',   35);
             
% Define colors
c = struct('ctrl',[0 0 0],'coloc',[1 0 0],'sep',[0 0.5 0]);                 % control
d = struct('ctrl',[0.5 0.5 0.5],'coloc',[1 0.4 0.4],'sep',[0.1 0.9 0.1]);   % cooled
