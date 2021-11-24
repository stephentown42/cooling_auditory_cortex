function TDTmultiSet(tag, val)

% Space saving function allows multiple parameter tags to be assigned
% values.

global DA gf 

for i = 1 : length(tags)
   
   if DA.SetTargetVal(sprintf('%s.%s', gf.stimDevice, tag{i}), val(i)) ~= 1,
       
       warning(sprintf('Failed to set %s.%s', gf.stimDevice, tag{i}))
   end
    
end

        