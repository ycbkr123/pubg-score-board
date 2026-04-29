<div class="box">
    <h3>4. 점수판 룰 설정</h3>
    <div class="config-row">
        <label>킬 점수: <input type="number" id="killScore" value="1" style="width: 50px;"></label>
        <label>데스 감점: <input type="number" id="deathPenalty" value="1" style="width: 50px;"></label>
        <label>목표 점수: <input type="number" id="targetScore" value="100" style="width: 70px;"></label>
        <label>종료 시간: <input type="time" id="endTime"></label>
    </div>
    <div class="config-row" style="margin-top: 10px; border-top: 1px solid #333; padding-top: 10px;">
        <span style="font-size: 0.9rem; color: #aaa;">치킨 점수 설정:</span>
        <label>에/미/태/데/론/비: <input type="number" id="chickenA" value="20" style="width: 50px;" title="에란겔, 미라마, 테이고, 데스턴, 론도, 비켄디"></label>
        <label>사/카/파: <input type="number" id="chickenB" value="15" style="width: 50px;" title="사녹, 카라킨, 파라모"></label>
    </div>
    <button class="btn-start" onclick="startGame()">팀 확정 및 대회 시작</button>
</div>

<div class="box" id="matchSection" style="display:none;">
    <div style="display: flex; justify-content: space-between; align-items: center;">
        <h3>진행 상황 <span id="clock" style="font-size: 1rem; color:#ffcc00; margin-left: 10px;"></span></h3>
        <div style="background: #f06414; padding: 10px 20px; border-radius: 8px; text-align: center;">
            <span style="font-size: 0.8rem; color: #eee; display: block;">전체 팀 합계 점수</span>
            <span id="totalScoreDisp" style="font-size: 1.8rem; font-weight: 900; color: #fff;">TOTAL 0</span>
        </div>
    </div>
    <p id="systemMsg">데이터 갱신 대기 중...</p>
    <div class="score-board" id="scoreBoard"></div>
    </div>

<script>
    // [중략] 이전과 동일한 변수 및 UI 로직

    function startGame() {
        // [중략] 팀 데이터 구성 로직 동일

        config = {
            killScore: parseInt(document.getElementById('killScore').value),
            deathPenalty: parseInt(document.getElementById('deathPenalty').value),
            targetScore: parseInt(document.getElementById('targetScore').value),
            endTime: document.getElementById('endTime').value,
            // 치킨 점수 설정값 가져오기
            chickenA: parseInt(document.getElementById('chickenA').value),
            chickenB: parseInt(document.getElementById('chickenB').value)
        };

        // [중략] 화면 전환 및 타이머 시작 로직 동일
    }

    // 치킨 점수 부여를 위한 맵 그룹 분류 [추론]
    const mapGroups = {
        groupA: ['Baltic_Main', 'Desert_Main', 'Tiger_Main', 'Kiki_Main', 'Neon_Main', 'DihorOtok_Main'], // 에/미/태/데/론/비
        groupB: ['Savage_Main', 'Summerland_Main', 'Chimera_Main'] // 사/카/파
    };

    function calculateScores(team, stats, matchMap) {
        let teamWonMatch = false;

        team.players.forEach(playerObj => {
            const matchedKey = Object.keys(stats).find(key => key.toLowerCase() === playerObj.name.toLowerCase());
            if (matchedKey) {
                const s = stats[matchedKey];
                const earned = (s.kills * config.killScore) - (s.deaths * config.deathPenalty);
                
                playerObj.kills += s.kills;
                playerObj.deaths += s.deaths;
                playerObj.score += earned;
                team.score += earned;

                // 해당 팀원 중 한 명이라도 승리(1등)했다면 팀 승리로 간주
                if (s.isWinner) teamWonMatch = true;
            }
        });

        // 치킨 점수 부여 [추론]
        if (teamWonMatch) {
            let chickenBonus = 0;
            if (mapGroups.groupA.includes(matchMap)) {
                chickenBonus = config.chickenA;
            } else if (mapGroups.groupB.includes(matchMap)) {
                chickenBonus = config.chickenB;
            }
            team.score += chickenBonus;
            // 대표 유저(팀장) 점수에 치킨 점수 합산 표기 (선택 사항)
            team.players[0].score += chickenBonus;
        }

        renderLiveScoreBoard();
        checkTargetScore();
    }

    function renderLiveScoreBoard() {
        const board = document.getElementById('scoreBoard');
        board.innerHTML = "";
        
        let totalScore = 0; // 전체 합계 계산

        teamsData.forEach(team => {
            totalScore += team.score;
            let playersHtml = team.players.map(p => `
                <div class="player-stats-row">
                    <span class="player-stats-name">${p.name}</span>
                    <span>${p.kills}K / ${p.deaths}D <span class="player-stats-score">(${p.score}점)</span></span>
                </div>
            `).join('');

            board.innerHTML += `
                <div class="live-team-card">
                    <h4>${team.name}</h4>
                    <h2>${team.score} 점</h2>
                    <div style="margin-top: 15px; text-align: left; background: #1a1c20; padding: 10px; border-radius: 8px;">
                        ${playersHtml}
                    </div>
                </div>
            `;
        });

        // TOTAL SCORE 업데이트
        document.getElementById('totalScoreDisp').innerText = `TOTAL ${totalScore}`;
    }
    
    // [중략] 나머지 통신 및 종료 로직 동일
</script>
