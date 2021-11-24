function C = filterData(B, masks)

if isempty(B)
    C = []; return
end

% Filter by noise type
isOk = B.SpatialMask == masks(1) | B.SpatialMask == masks(2);
C    = B(isOk,:);  % Apply filter