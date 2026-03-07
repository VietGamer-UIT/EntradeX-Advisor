#pragma once
#include "MarketDataFetcher.h"

class SmartAdvisorBot {
private:
    double baseBudget;
    MarketDataFetcher dataFetcher;
public:
    SmartAdvisorBot(double budget);
    void advise();
};