#!/bin/bash
# Full Test Suite Runner
# Team: Let It Fly - MY AI Hackathon 2025

API_URL="https://bteng7ing0.execute-api.ap-southeast-1.amazonaws.com/prod/chat"
OUTPUT_DIR="/tmp/test_output"
RESULTS_CSV="$OUTPUT_DIR/results.csv"

mkdir -p "$OUTPUT_DIR"
rm -f "$OUTPUT_DIR"/*.json 2>/dev/null

echo "test_id|phone|message|status|latency_ms|grounded|language|requires_followup|response_preview" > "$RESULTS_CSV"

run_test() {
    local tid="$1"
    local phone="$2"
    local msg="$3"
    
    local start=$(python3 -c "import time; print(int(time.time()*1000))")
    local resp=$(curl -s -X POST "$API_URL" -H "Content-Type: application/json" -d "{\"message\":\"$msg\",\"phone_number\":\"$phone\"}" 2>/dev/null)
    local end=$(python3 -c "import time; print(int(time.time()*1000))")
    local lat=$((end - start))
    
    echo "$resp" > "$OUTPUT_DIR/$tid.json"
    
    local grounded=$(echo "$resp" | python3 -c "import json,sys; d=json.load(sys.stdin); print(d.get('metadata',{}).get('grounded','N/A'))" 2>/dev/null || echo "N/A")
    local lang=$(echo "$resp" | python3 -c "import json,sys; d=json.load(sys.stdin); print(d.get('metadata',{}).get('language','N/A'))" 2>/dev/null || echo "N/A")
    local followup=$(echo "$resp" | python3 -c "import json,sys; d=json.load(sys.stdin); print(d.get('requires_followup','N/A'))" 2>/dev/null || echo "N/A")
    local preview=$(echo "$resp" | python3 -c "import json,sys; d=json.load(sys.stdin); m=d.get('message','ERROR'); print(m[:80] if len(m)>80 else m)" 2>/dev/null || echo "ERROR")
    
    local status="PASS"
    if [[ "$preview" == "ERROR" ]] || [[ -z "$resp" ]]; then status="FAIL"; fi
    
    echo "$tid|$phone|$msg|$status|$lat|$grounded|$lang|$followup|$preview" >> "$RESULTS_CSV"
    echo "  $tid: $status (${lat}ms) [grounded=$grounded, lang=$lang]"
}

echo "=========================================="
echo "MY AI Hackathon 2025 - Full Test Suite"
echo "API: $API_URL"
echo "Started: $(date)"
echo "=========================================="
echo ""

# Category A: English KB Queries (10 tests)
echo "=== Category A: English KB Queries (10 tests) ==="
run_test "EN-KB-01" "+60132211009" "What is voicemail?"
sleep 5
run_test "EN-KB-02" "+60132211009" "How do I deactivate my voicemail?"
sleep 5
run_test "EN-KB-03" "+60129988771" "How to activate voicemail service?"
sleep 5
run_test "EN-KB-04" "+60132211009" "How much does voicemail cost?"
sleep 5
run_test "EN-KB-05" "+60132211009" "How do I check my voicemail messages?"
sleep 5
run_test "EN-KB-06" "+60132211009" "How many messages can voicemail store?"
sleep 5
run_test "EN-KB-07" "+60132211009" "Does voicemail work when roaming?"
sleep 5
run_test "EN-KB-08" "+60132211009" "What happens to old voicemail messages?"
sleep 5
run_test "EN-KB-09" "+60132211009" "How long can a voicemail message be?"
sleep 5
run_test "EN-KB-10" "+60132211009" "Is voicemail free for postpaid?"
sleep 5

# Category B: Bahasa Malaysia KB Queries (8 tests)
echo ""
echo "=== Category B: BM KB Queries (8 tests) ==="
run_test "BM-KB-01" "+60168899001" "Apa itu mel suara?"
sleep 5
run_test "BM-KB-02" "+60168899001" "Macam mana nak nyahaktifkan mel suara?"
sleep 5
run_test "BM-KB-03" "+60183344552" "Bagaimana untuk aktifkan mel suara?"
sleep 5
run_test "BM-KB-04" "+60168899001" "Berapa harga mel suara?"
sleep 5
run_test "BM-KB-05" "+60168899001" "Bagaimana nak dengar mesej mel suara?"
sleep 5
run_test "BM-KB-06" "+60168899001" "Berapa banyak mesej boleh disimpan?"
sleep 5
run_test "BM-KB-07" "+60168899001" "Mel suara ada ke bila saya di luar negara?"
sleep 5
run_test "BM-KB-08" "+60168899001" "Mesej mel suara kena hapus automatik ke?"
sleep 5

# Category C: Slang & Code-Mixed Queries (10 tests)
echo ""
echo "=== Category C: Slang & Code-Mixed (10 tests) ==="
run_test "SLANG-01" "+60132211009" "nk off vm plss"
sleep 5
run_test "SLANG-02" "+60168899001" "tolong matikan mel suara sy"
sleep 5
run_test "SLANG-03" "+60132211009" "vm x jln la, nk tutup"
sleep 5
run_test "SLANG-04" "+60132211009" "cmne nk check vm?"
sleep 5
run_test "SLANG-05" "+60132211009" "brp harga vm ni?"
sleep 5
run_test "SLANG-06" "+60132211009" "pls activate my vm nowww"
sleep 5
run_test "SLANG-07" "+60168899001" "sy nk on vm blk"
sleep 5
run_test "SLANG-08" "+60132211009" "vm sy aktif ke x?"
sleep 5
run_test "SLANG-09" "+60132211009" "helppp dgn vm sy"
sleep 5
run_test "SLANG-10" "+60132211009" "i nk off kan ni skrg"
sleep 5

# Category D: CRM Operations (8 tests)
echo ""
echo "=== Category D: CRM Operations (8 tests) ==="
run_test "CRM-DEACT-01" "+60132211009" "I want to turn off my voicemail"
sleep 5
run_test "CRM-DEACT-02" "+60132211009" "deactivate voicemail, my PIN is 1234"
sleep 5
run_test "CRM-DEACT-03" "+60132211009" "off vm, PIN 0000"
sleep 5
run_test "CRM-DEACT-04" "+60168899001" "matikan mel suara saya, PIN 4321"
sleep 5
run_test "CRM-ACT-01" "+60129988771" "I want to activate voicemail"
sleep 5
run_test "CRM-ACT-02" "+60129988771" "tolong aktifkan vm sy, PIN 9999"
sleep 5
run_test "CRM-STATUS-01" "+60132211009" "Is my voicemail active?"
sleep 5
run_test "CRM-STATUS-02" "+60168899001" "vm sy aktif ke?"
sleep 5

# Category E: Human Escalation (8 tests)
echo ""
echo "=== Category E: Escalation Triggers (8 tests) ==="
run_test "ESC-01" "+60132211009" "I want to speak to a human agent"
sleep 5
run_test "ESC-02" "+60132211009" "transfer me to customer service"
sleep 5
run_test "ESC-03" "+60168899001" "saya nak cakap dengan orang"
sleep 5
run_test "ESC-04" "+60168899001" "boleh connect dengan agent?"
sleep 5
run_test "ESC-05" "+60132211009" "How do I pay my phone bill?"
sleep 5
run_test "ESC-06" "+60132211009" "I want to change my data plan"
sleep 5
run_test "ESC-07" "+60132211009" "Where is the nearest store?"
sleep 5
run_test "ESC-08" "+60168899001" "nak tukar sim card"
sleep 5

# Category F: Out-of-KB (3 tests)
echo ""
echo "=== Category F: Out-of-KB Queries (3 tests) ==="
run_test "OOK-01" "+60132211009" "Can I forward my voicemail to email?"
sleep 5
run_test "OOK-02" "+60132211009" "How to set custom voicemail greeting?"
sleep 5
run_test "OOK-03" "+60132211009" "Is there voicemail transcription?"
sleep 5

# Category G: Greetings (3 tests)
echo ""
echo "=== Category G: Greetings (3 tests) ==="
run_test "GEN-01" "+60132211009" "Hi"
sleep 5
run_test "GEN-02" "+60132211009" "Hello, I need help"
sleep 5
run_test "GEN-03" "+60168899001" "Hai, saya perlukan bantuan"
sleep 5

# Category H: Multi-turn Flows (8 tests - requires followup handling)
echo ""
echo "=== Category H: Multi-Turn Flows (8 tests) ==="
# H1: English deactivation flow
run_test "FLOW-EN-01a" "+60132211009" "I want to deactivate my voicemail"
sleep 5
run_test "FLOW-EN-01b" "+60132211009" "My PIN is 1234"
sleep 5

# H2: BM deactivation flow  
run_test "FLOW-BM-01a" "+60168899001" "saya nak matikan mel suara"
sleep 5
run_test "FLOW-BM-01b" "+60168899001" "PIN saya 4321"
sleep 5

# H3: Wrong PIN retry flow
run_test "FLOW-PIN-01a" "+60132211009" "off vm please"
sleep 5
run_test "FLOW-PIN-01b" "+60132211009" "PIN 0000"
sleep 5
run_test "FLOW-PIN-01c" "+60132211009" "sorry, PIN 1234"
sleep 5

# H4: Activation flow
run_test "FLOW-ACT-01a" "+60129988771" "please activate my voicemail"
sleep 5
run_test "FLOW-ACT-01b" "+60129988771" "9999"

echo ""
echo "=========================================="
echo "Test Suite Complete!"
echo "Finished: $(date)"
echo "=========================================="
echo ""
echo "Results saved to: $RESULTS_CSV"
echo ""

# Generate summary
echo "=== SUMMARY ==="
TOTAL=$(tail -n +2 "$RESULTS_CSV" | wc -l | tr -d ' ')
PASSED=$(tail -n +2 "$RESULTS_CSV" | grep "|PASS|" | wc -l | tr -d ' ')
FAILED=$(tail -n +2 "$RESULTS_CSV" | grep "|FAIL|" | wc -l | tr -d ' ')
echo "Total Tests: $TOTAL"
echo "Passed: $PASSED"
echo "Failed: $FAILED"

# Copy results to project
cp "$RESULTS_CSV" /Users/kita/Desktop/BreakIntoAI/Let-It-Fly/test_results.csv


