#include "SmartAdvisorBot.h"
#include <iostream>
#include <iomanip>

using namespace std;

SmartAdvisorBot::SmartAdvisorBot(double budget) : baseBudget(budget) {};

void SmartAdvisorBot::advise() {
    cout << "\n======================================================\n";
    cout << "       [ ENTRADE X by DNSE - SMART ADVISOR ]          \n";
    cout << "======================================================\n";

    double currentPE = dataFetcher.fetchPE();
    double currentRate = dataFetcher.fetchInterestRate();
    double currentPrice = dataFetcher.fetchE1Price();

    cout << "\n[Hệ thống] Dang dong bo du lieu vi mo & Giai thuat Smart DCA...\n";
    double moneyToInvest = 0;

    // Logic cốt lõi
    if (currentPE < 11.0 || currentRate > 8.0) {
        cout << ">> TIN HIEU: THI TRUONG GAU (BEAR MARKET) - DINH GIA RE!\n";
        moneyToInvest = baseBudget * 2;
    }
    else if (currentPE >= 11.0 && currentPE <= 15.0) {
        cout << ">> TIN HIEU: THI TRUONG BO (BULL MARKET) - ON DINH.\n";
        moneyToInvest = baseBudget * 0.8;
    }
    else {
        cout << ">> TIN HIEU: THI TRUONG BONG BONG - CAN PHONG THU.\n";
        moneyToInvest = baseBudget * 0.4;
    }

    int volumeToBuy = moneyToInvest / currentPrice;
    double actualCost = volumeToBuy * currentPrice;
    double moneyToSave = baseBudget - actualCost;

    // IN RA GIAO DIỆN BIÊN LAI ĐẶT LỆNH ĐỘC QUYỀN ENTRADE X
    cout << "\n------------------------------------------------------\n";
    cout << "      [PHIEU LENH KHUYEN NGHI - ENTRADE X APP]        \n";
    cout << "------------------------------------------------------\n";
    cout << " Tieu khoan       : Thuong (Duoi 1)\n";
    cout << " Ma chung khoan   : E1VFVN30 (VN30 ETF)\n";
    cout << " Loai lenh        : MUA (Ho tro Khop lenh Lo le)\n";
    cout << " Khoi luong Mua   : " << volumeToBuy << " ccq (chung chi quy)\n";
    cout << " Gia dat (Tam tinh): " << fixed << setprecision(0) << currentPrice << " VND\n";
    cout << " Phi giao dich    : 0 VND (Mien phi tron doi)\n";
    cout << " Thue (Mua)       : 0 VND\n";
    cout << "------------------------------------------------------\n";
    cout << " TONG GIA TRI LENH: " << actualCost << " VND\n";

    if (actualCost < baseBudget) {
        cout << " TIEN DU PHONG    : " << moneyToSave << " VND\n";
        cout << " (=> So tien nay duoc tu dong Sinh lai qua dem tren app)\n";
    }
    else {
        cout << " [!] DCA TANG TOC : Can bo sung them tien tu Quy du phong!\n";
    }
    cout << "======================================================\n";
    cout << "Thao tac tiep theo: Mo app Entrade X -> Tim ma E1VFVN30 -> Nhap so luong -> MUA.\n";
}