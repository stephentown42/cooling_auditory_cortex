function sp = create_figure( file_name);


% New figure
figure('name',file_name)
sp(1) = subplot(2,3,1); title('Signal Only')
sp(2) = subplot(2,3,2); title('Colocalized')
sp(3) = subplot(2,3,3); title('Separated')
sp(4) = subplot(2,3,4); title('Across Attn')
sp(5) = subplot(2,3,5); title('Control')
sp(6) = subplot(2,3,6); title('Cooled')

set(sp,'nextPlot','add','ylim',[40 100],'FontSize',9);   % Hold on 

for j = 1 : numel(sp)
    ylabel(sp(j),'% Correct')
    xlabel(sp(j),'Attenuation (dB)')
end