# Implementacja modelu Rabbits Grass Weeds w Python

library(plyr)
library(lattice)

# Zaimportowanie zbioru utworzonego w Python
wyniki <- read.csv("lokalizacja_zrodlowa\\rabbit_wyniki.csv")
zlim <- range(wyniki$rab_number)
zlen <- zlim[2] - zlim[1] + 1

## Srednie liczby krolikow w populacji w zaleznosci od pogrupowania

# Pogrupowanie po grass_dt i rab_energy
sum.data = ddply(wyniki, .( grass_dt, rab_energy), summarize,
                 m_rab_number = mean(rab_number),
                 sd_rab_number = sd(rab_number))
sum.data <- sum.data[order(sum.data$grass_dt, sum.data$rab_energy),]
head(sum.data)

# Pogrupowanie po grass_dt i weed_dt
sum.data1 = ddply(wyniki, .( grass_dt, weed_dt), summarize,
                 m_rab_number = mean(rab_number),
                 sd_rab_number = sd(rab_number))
sum.data1 <- sum.data1[order(sum.data1$grass_dt, sum.data1$weed_dt),]
head(sum.data1)

# Pogrupowanie po weed_dt i rab_energy
sum.data2 = ddply(wyniki, .( weed_dt, rab_energy), summarize,
                 m_rab_number = mean(rab_number),
                 sd_rab_number = sd(rab_number))
sum.data2 <- sum.data2[order(sum.data2$weed_dt, sum.data2$rab_energy),]
head(sum.data2)

## Utworzenie nowego zbioru danych do predykcji metamodelu
grass_range <- range(wyniki$grass_dt)      
weed_range <- range(wyniki$weed_dt) 
energy_range <- range(wyniki$rab_energy) 
grassrange <-   seq(grass_range[1], grass_range[2], by=0.01)
weedrange <- seq(weed_range[1], weed_range[2], by=0.01)
energyrange <- seq(energy_range[1], energy_range[2])
new.data <- expand.grid(grassrange, weedrange, energyrange)
colnames(new.data) <- c("grass_dt", "weed_dt", "rab_energy")
head(new.data)
rm(grass_range)
rm(grassrange)
rm(weed_range)
rm(weedrange)
rm(energy_range)
rm(energyrange)


# Zbudowany metamodel (Regresja liniowa)
model1 <- lm(rab_number ~ grass_dt + weed_dt + rab_energy, data = wyniki)
summary(model1)

### Wszystkie zmienne objasniajace sa istotne w modelu ###

# Wizualizacja
new.data$num_hat <- predict(model1, newdata = new.data)
contourplot(num_hat ~ grass_dt + weed_dt + rab_energy, data = new.data,
            cuts = 20, region = T, col.regions = terrain.colors(zlen))
wireframe(num_hat ~ grass_dt + weed_dt + rab_energy, data = new.data,
          drape = TRUE, colorkey = TRUE, pretty = T, region = T,
          cuts = 10, region = T, col.regions = terrain.colors(zlen))

