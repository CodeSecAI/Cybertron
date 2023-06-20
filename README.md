# Cybertron
Beta release of Cybertron Model


## Setup

```
pip install langchain
```
### Example run
```
 python .\PenTestTool.py -m model.jsonl -t -p train -P train --provider azure --azure-model CodeSec --mode code-review -f ".c"
Loaded 2534 records from model.jsonl
CodeSec.ai Training Model Complete
---------------------------
Testing: train\23-bufferOverflow.c
Title: Buffer Overflow Vulnerability
Description: The code is a C program that takes user input for a One-Time Password (OTP) and compares it to a pre-defined OTP. The OTP is obtained from the GetOTP() function. The program allows the user to enter the OTP three times before terminating.
Issue: The program uses the gets() function to read user input into the tryOTP buffer, which can lead to a buffer overflow vulnerability. The buffer is only allocated 4 bytes, but gets() does not check the size of the input, which can lead to overwriting adjacent memory.
Threat Model: The vulnerability can be exploited using the Spoofing, Tampering, and Elevation of Privilege (STEEP) methods of the STRIDE methodology.
Proof of Concept: To test the vulnerability, an attacker can input more than 4 characters as the OTP. This will cause the buffer to overflow and potentially overwrite adjacent memory. A proof of concept script is provided below:


#!/bin/bash
echo -n "Enter OTP (Five digits): "
python -c 'print "A"*5' | ./23-bof
```

Taint Analysis: The input from gets() is directly stored in the tryOTP buffer, which is then used in the strcmp() function. This means that any input that overflows the buffer can potentially overwrite adjacent memory and modify the behavior of the program.

Recommendation: To remediate the vulnerability, the gets() function should be replaced with a safer alternative such as fgets(). Additionally, the tryOTP buffer should be allocated with a size that can accommodate the maximum input length. The modified code is shown below:

```
#include <stdio.h>
#include <string.h>

char* GetOTP(){
    //Code...
    //Example OPT code return:
    return "1337";
}

/**
 * YesWeHack - Vulnerable Code Snippet
*/

// Run: gcc 23-bufferOverflow.c -fno-stack-protector -o 23-bof
// Then run the program: ./23-bof

// If that do not work, run: `chmod +x 23-bufferOverflow.c`. Then run it again

int LoadDashboard(){}

int main(void)
{
    char *OTP = GetOTP();
    char tryOTP[6];
    int root = 0;

    for ( int tries = 0; tries < 3; tries++ ) {
        printf("Enter OTP (Five digits): ");
        fgets(tryOTP, 6, stdin);
        tryOTP[strcspn(tryOTP, "\n")] = 0; // remove trailing newline

        //Check if the user has root privileges or OPT:
        if ( root || strcmp(tryOTP, OTP) == 0 ) {
            printf("> Success, loading dashboard\n");
            LoadDashboard();
            return 1;
        } else {
            printf ("> Incorrect OTP\n");
        }

        if ( tries >= 3 ) {
            return 0;
        }
    }
}
```

Taxonomy: The vulnerability is a CWE-119: Improper Restriction of Operations within the Bounds of a Memory Buffer and a CAPEC-242: Buffer Overflow via Environment Variables.

CVSS Score: The CVSS3.1 score for this vulnerability is 7.8 (High).
