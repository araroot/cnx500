require(plyr)
require(ggplot2)
library(Hmisc)

analyze.yr <- function(df.in, yr) {
  my.df <- subset(df.in, stamp %in% paste(yr,sprintf('%02d',c(1:12)),sep=''))
  my.df$last_9 <- with(my.df, r1+r2+r3+r4+r5+r6+r7+r8+r9)
  my.df$last_3 <- with(my.df, r1+r2+r3)
  
  df.out <- ddply(my.df, .(stamp), transform, Grp9 = factor(cut2(last_9, g=10), labels=c(1:10)))
  #df.out <- ddply(my.df, .(stamp), transform, Grp3 = factor(cut2(last_3, g=10), labels=c(1:10)))
  
  df.out <- df.out[complete.cases(df.out),]
  return(df.out)
}