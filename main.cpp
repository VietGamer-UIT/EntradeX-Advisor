#include <iostream>
#include "SmartAdvisorBot.h"

using namespace std;

int main() {
    // Cài đặt ngân sách cố định là 500k / tháng (có thể tùy chỉnh)
    SmartAdvisorBot myBot(500000);

    myBot.advise();

    cout << "\n[He thong] Nhan Enter de ket thuc...";
    cin.ignore();
    cin.get();
    return 0;
}