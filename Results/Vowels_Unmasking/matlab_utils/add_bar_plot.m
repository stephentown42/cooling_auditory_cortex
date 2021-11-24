function add_bar_plot(sp, COctrl, COcool, SPctrl, SPcool, SOctrl, SOcool)

    % Bar plot
    myBar = @(x) mean(x).*100;
    axes(sp(4))
    
    b(1) = bar(1, myBar(SOctrl.Correct),'FaceColor','k');
    b(2) = bar(2, myBar(SOcool.Correct),'FaceColor',[0.5 0.5 0.5]);
    b(3) = bar(4, myBar(SPctrl.Correct),'FaceColor',[0 0.5 0]);
    b(4) = bar(5, myBar(SPcool.Correct),'FaceColor',[0.1 0.9 0.1]);
    b(5) = bar(7, myBar(COctrl.Correct),'FaceColor','r');
    b(6) = bar(8, myBar(COcool.Correct),'FaceColor',[1.0 0.4 0.4]);
    
    set(sp(4),'xtick',2:3:8,'xticklabel',{'Signal only','Separated','Colocalized'})
    