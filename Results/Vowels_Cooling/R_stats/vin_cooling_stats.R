# Analysis of effects of cortical inactivation on vowel discrimination in noise using logistic regression  

# Following the example given in:
# http://rstudio-pubs-static.s3.amazonaws.com/74431_8cbd662559f6451f9cd411545f28107f.html
#
#
# Version History:
#   Created: 2021-09-09 Stephen Town

# Clear all 
rm(list = ls())

# library(caret)        # for cross-validation
library(lme4)           # for mixed model
library(stargazer)      # for reporting mixed models
library(scales)         # for rescaling signal level

# Load data and combine across subjects 
data_path = 'Results/Vowels_Cooling/data/analysis'

magnum = read.csv( file.path( data_path, 'F1311.csv'))
robin  = read.csv( file.path( data_path, 'F1509.csv'))
mimi   = read.csv( file.path( data_path, 'F1706.csv'))


cols = c('fNum','treatment',"vowel","Mask","Correct","vowel_level","SNR")

df = rbind(magnum[cols], robin[cols], mimi[cols])

df$reLevel <- rescale(df$vowel_level)


# Connect to text file for output
output_file = file.path('Results/Vowels_Cooling', "vowel_in_noise_cooling_stats_report.txt")
sink(output_file)

print('Analysis run at:')
print(Sys.time())
print('########################################################')
print('########################################################')
print('########################################################')

# Run logistic regression
# full_mdl <- glmer(Correct ~ treatment*Mask + (1|fNum/sessionDate), data=df, family=binomial)
# summary(full_mdl)

# Examine how dependent the outcome is on random effects organization                   <==== Currently reported in the manuscript
full_noSess <- glmer(Correct ~ treatment*Mask*SNR + (1|fNum), data=df, family=binomial)

print('Bilateral cooling')
print(summary(full_noSess))
# (2021-09-09: Get similar results with or without session date)

# Examine how dependent the outcome is on random effects organization
# full_SNRrand <- glmer(Correct ~ treatment*Mask + (1|fNum) + (1|SNR), data=df, family=binomial)
# summary(full_SNRrand)
# 2021-09-09: Get similar results as models above 

# Add level (as rescaled)
# full_levelFE <- glmer(Correct ~ treatment*Mask + reLevel + reLevel*Mask+ (1|fNum), data=df, family=binomial)
# summary(full_levelFE)





#################################################################################
# Sanity checks to confirm intuitions from data visualization (see python code)

# Clean conditions only
# clean = df[df['Mask'] == 'Clean',]
# clean_mdl <- glmer(Correct ~ treatment + (1|fNum/sessionDate), data=clean, family=binomial)
# summary(clean_mdl)


# noise = df[df['Mask'] == 'Restricted',]

# noise_mdl <- glmer(Correct ~ treatment * SNR + (1|fNum), data=noise, family=binomial)
# print(summary(noise_mdl))

# ################################################################################
# # Visualize model

# sim = data.frame(Mask=integer(), treatment=logical(), fNum=integer())

# df$predict <- predict(full_noSess, newdata=df, type="response")


# ggplot(df, aes(x=SNR, y=Coast)) + geom_line()
# c_mdl <- glmer(Correct ~ treatment, data=df, family=binomial)
# c_mdl <- glmer(Correct ~ treatment + (1|fNum), data=df, family=binomial)
# summary(c_mdl)



########################################################
# Return control to console
sink()  