// puzzle.js — frontend controller and board animator

// app state
let currentBoard = [1, 2, 5, 3, 4, 0, 6, 7, 8];
let solutionPath = [];
let solutionMoves = [];
let currentStep = 0;
let isPlaying = false;
let playInterval = null;
const playSpeed = 900;

// dom elements
const boardEl = document.getElementById('board');
const stepCounterEl = document.getElementById('step-counter');
const moveStatusEl = document.getElementById('move-status');
const alertBoxEl = document.getElementById('alert-box');
const inputEl = document.getElementById('initial-state-input');
const pathListEl = document.getElementById('path-list');

const statMovesEl = document.getElementById('stat-moves');
const statCostEl = document.getElementById('stat-cost');
const statNodesEl = document.getElementById('stat-nodes');
const statDepthEl = document.getElementById('stat-depth');
const statTimeEl = document.getElementById('stat-time');

const btnPrev = document.getElementById('btn-prev');
const btnPlay = document.getElementById('btn-play');
const btnNext = document.getElementById('btn-next');
const btnSolve = document.getElementById('btn-solve');
const btnReset = document.getElementById('btn-reset');
const btnRandom = document.getElementById('btn-random');

const tracePanelEl = document.getElementById('trace-panel');
const traceBodyEl = document.getElementById('trace-body');
const traceNoteEl = document.getElementById('trace-note');

// render 3x3 board
function renderBoard(board, highlightTile = null) {
  boardEl.innerHTML = '';

  board.forEach((val, idx) => {
    const tile = document.createElement('div');
    tile.classList.add('tile');

    if (val === 0) {
      tile.classList.add('blank');
      tile.textContent = '';
    } else {
      tile.textContent = val;
      tile.dataset.val = val;
      if (val === highlightTile) {
        tile.classList.add('highlight');
      }
      // allow clicking to move tile if adjacent to blank space
      tile.addEventListener('click', () => handleManualMove(idx));
    }
    boardEl.appendChild(tile);
  });
}

// manual tile movement on click
function handleManualMove(tileIdx) {
  if (isPlaying) return;
  const blankIdx = currentBoard.indexOf(0);

  const tileRow = Math.floor(tileIdx / 3);
  const tileCol = tileIdx % 3;
  const blankRow = Math.floor(blankIdx / 3);
  const blankCol = blankIdx % 3;

  const isAdjacent = (Math.abs(tileRow - blankRow) + Math.abs(tileCol - blankCol)) === 1;
  if (isAdjacent) {
    const movedVal = currentBoard[tileIdx];
    currentBoard[blankIdx] = movedVal;
    currentBoard[tileIdx] = 0;
    inputEl.value = currentBoard.join(', ');
    clearSolution();
    renderBoard(currentBoard, movedVal);

    // check if user solved it by hand
    const isGoal = currentBoard.every((val, i) => val === i);
    if (isGoal) {
      showAlert('good job! you solved it by hand, well done! :)', 'success');
      moveStatusEl.textContent = 'solved by hand! well done! :)';
    }
  }
}

// parse input state from text field
function parseInputState() {
  const parts = inputEl.value.split(',').map(s => parseInt(s.trim(), 10));
  if (parts.length !== 9 || parts.some(isNaN)) {
    showAlert('enter 9 numbers separated by commas', 'error');
    return null;
  }
  const sorted = [...parts].sort((a, b) => a - b);
  for (let i = 0; i < 9; i++) {
    if (sorted[i] !== i) {
      showAlert('must contain numbers 0 through 8 with no duplicates', 'error');
      return null;
    }
  }
  hideAlert();
  return parts;
}

// generate random solvable board by walking backwards from goal
function generateRandomSolvable() {
  let board = [0, 1, 2, 3, 4, 5, 6, 7, 8];
  const moves = [
    [-1, 0], [1, 0], [0, -1], [0, 1]
  ];

  for (let step = 0; step < 24; step++) {
    const blank = board.indexOf(0);
    const r = Math.floor(blank / 3);
    const c = blank % 3;

    const validMoves = [];
    moves.forEach(([dr, dc]) => {
      const nr = r + dr, nc = c + dc;
      if (nr >= 0 && nr < 3 && nc >= 0 && nc < 3) {
        validMoves.push(nr * 3 + nc);
      }
    });

    const targetIdx = validMoves[Math.floor(Math.random() * validMoves.length)];
    board[blank] = board[targetIdx];
    board[targetIdx] = 0;
  }

  currentBoard = board;
  inputEl.value = board.join(', ');
  renderBoard(currentBoard);
  clearSolution();
  showAlert('generated solvable state', 'success');
}

// update controls and labels
function updatePlaybackUI() {
  const hasPath = solutionPath.length > 0;

  btnPrev.disabled = !hasPath || currentStep === 0 || isPlaying;
  btnNext.disabled = !hasPath || currentStep >= solutionPath.length - 1 || isPlaying;
  btnPlay.disabled = !hasPath;

  if (hasPath) {
    stepCounterEl.textContent = `Step ${currentStep} / ${solutionPath.length - 1}`;

    if (currentStep === 0) {
      moveStatusEl.textContent = 'Initial state';
    } else {
      const prevBoard = solutionPath[currentStep - 1];
      const oldBlank = prevBoard.indexOf(0);
      const movedTile = solutionPath[currentStep][oldBlank];
      const move = solutionMoves[currentStep - 1] || 'move';
      moveStatusEl.textContent = `Step ${currentStep}: Tile ${movedTile} moved ${move} into blank`;
    }

    const chips = pathListEl.querySelectorAll('.step-chip');
    chips.forEach((c, idx) => {
      c.classList.toggle('active', idx === currentStep);
    });
  } else {
    stepCounterEl.textContent = 'Step 0 / 0';
    moveStatusEl.textContent = 'Initial state';
  }
}

// jump to a step
function goToStep(index) {
  if (index < 0 || index >= solutionPath.length) return;
  currentStep = index;
  currentBoard = solutionPath[currentStep];

  // determine which tile moved from the previous step into the blank space
  let movedTile = null;
  if (currentStep > 0 && solutionPath[currentStep - 1]) {
    const oldBlank = solutionPath[currentStep - 1].indexOf(0);
    movedTile = currentBoard[oldBlank];
  }

  renderBoard(currentBoard, movedTile);
  updatePlaybackUI();
}

// playback control
function togglePlay() {
  if (isPlaying) {
    pause();
  } else {
    play();
  }
}

function play() {
  if (solutionPath.length === 0) return;
  if (currentStep >= solutionPath.length - 1) {
    currentStep = 0;
  }

  isPlaying = true;
  btnPlay.textContent = 'Pause';
  updatePlaybackUI();

  playInterval = setInterval(() => {
    if (currentStep < solutionPath.length - 1) {
      goToStep(currentStep + 1);
    } else {
      pause();
    }
  }, playSpeed);
}

function pause() {
  isPlaying = false;
  clearInterval(playInterval);
  btnPlay.textContent = 'Play';
  updatePlaybackUI();
}

// reset solution state
function clearSolution() {
  pause();
  solutionPath = [];
  solutionMoves = [];
  currentStep = 0;
  updatePlaybackUI();

  statMovesEl.textContent = '—';
  statCostEl.textContent = '—';
  statNodesEl.textContent = '—';
  statDepthEl.textContent = '—';
  statTimeEl.textContent = '—';

  pathListEl.innerHTML = '<span class="muted">No solution loaded.</span>';

  // restore flex so path trace panel stretches to match results panel height
  const pathPanel = document.querySelector('.main-column .panel:last-child');
  if (pathPanel) pathPanel.style.flex = '1';
  clearTrace();
}

// render step list
function renderPathList() {
  // release flex so panel sizes to its content after solve
  const pathPanel = document.querySelector('.main-column .panel:last-child');
  if (pathPanel) pathPanel.style.flex = 'none';

  pathListEl.innerHTML = '';
  solutionPath.forEach((_, idx) => {
    const chip = document.createElement('span');
    chip.classList.add('step-chip');
    chip.textContent = idx === 0 ? 'Start' : `${solutionMoves[idx - 1] || idx}`;
    chip.addEventListener('click', () => {
      pause();
      goToStep(idx);
    });
    pathListEl.appendChild(chip);
  });
}

// ---------- search trace ----------
const CHILD_STATUS = {
  queued: 'added to frontier',
  explored: 'skipped: already explored',
  visited: 'skipped: already visited',
  worse: 'skipped: cheaper path queued',
  cycle: 'skipped: already on current path',
  goal: 'goal reached',
};

function makeEl(tag, cls, text) {
  const e = document.createElement(tag);
  if (cls) e.className = cls;
  if (text !== undefined) e.textContent = text;
  return e;
}

// small 3x3 board; movedIdx outlines the tile that just moved
function miniBoard(board, small = false, movedIdx = null) {
  const wrap = makeEl('div', 'mini-board' + (small ? ' sm' : ''));
  board.forEach((val, idx) => {
    const cell = makeEl('div', 'tile mini-cell');
    if (val === 0) {
      cell.classList.add('blank');
    } else {
      cell.textContent = val;
      cell.dataset.val = val;
      if (idx === movedIdx) cell.classList.add('highlight');
    }
    wrap.appendChild(cell);
  });
  return wrap;
}

function costBadges(g, h, f) {
  const row = makeEl('div', 'node-costs');
  [['g', g], ['h', h], ['f', f]].forEach(([k, v]) => {
    row.appendChild(makeEl('span', `cost cost-${k}`, `${k}=${v ?? '—'}`));
  });
  return row;
}

function clearTrace() {
  traceBodyEl.innerHTML = '';
  traceNoteEl.textContent = '';
  tracePanelEl.open = false;
  tracePanelEl.classList.add('hidden');
}

function renderTrace(trace) {
  clearTrace();
  if (!trace) return;
  tracePanelEl.classList.remove('hidden');

  // heuristic first
  if (trace.heuristic) {
    traceBodyEl.appendChild(
      makeEl('div', 'trace-head', `Heuristic: ${trace.heuristic} | h(start) = ${trace.initial_h}`)
    );
  }

  trace.steps.forEach((s, i) => {
    const d = makeEl('details', 'trace-step');
    if (i === 0) d.open = true;
    d.appendChild(makeEl(
      'summary', null,
      `Step ${s.step}` + (s.label ? ` [${s.label}]` : '') +
      (s.goal ? ' | goal reached' : ' | expand node') +
      (s.f !== undefined ? ` (f=${s.f})` : ` (depth=${s.g})`)
    ));

    const tree = makeEl('div', 'tree');

    // the expanded node
    const node = makeEl('div', 'node node-parent' + (s.goal ? ' node-goal' : ''));
    node.appendChild(makeEl('div', 'node-title', s.goal ? 'Goal' : 'Expanded node'));
    node.appendChild(miniBoard(s.board));
    node.appendChild(costBadges(s.g, s.h, s.f));
    tree.appendChild(node);

    // its children
    if (s.children && s.children.length) {
      tree.appendChild(makeEl('div', 'tree-stem'));
      const row = makeEl('div', 'tree-children');
      const blankIdx = s.board.indexOf(0);   // the tile that moved now sits here in the child
      s.children.forEach(c => {
        const col = makeEl('div', 'tree-child');
        const card = makeEl('div', `node node-${c.status}`);
        card.appendChild(makeEl('div', 'node-title', c.move));
        card.appendChild(miniBoard(c.board, false, blankIdx));
        card.appendChild(costBadges(c.g, c.h, c.f));
        card.appendChild(makeEl('div', 'node-status', CHILD_STATUS[c.status] || c.status));
        col.appendChild(card);
        row.appendChild(col);
      });
      tree.appendChild(row);
    }
    d.appendChild(tree);

    // contents of the data structure
    if (s.frontier) {
      const nextLast = trace.next_at === 'last';     // stacks: the next item is the last card
      d.appendChild(makeEl(
        'div', 'trace-label',
        `${trace.structure || 'Frontier'} after this step: ${s.frontier_size} entries, explored: ${s.explored_size}` +
        (s.frontier.length < s.frontier_size ? ` (showing ${nextLast ? 'top' : 'first'} ${s.frontier.length})` : '')
      ));
      const fr = makeEl('div', 'frontier-row');
      const m = s.frontier.length;
      s.frontier.forEach((e, k) => {
        const order = nextLast ? m - k : k + 1;      // 1 = the next one to leave the structure
        const item = makeEl('div', 'node frontier-item' + (order === 1 ? ' frontier-next' : ''));
        item.appendChild(makeEl('div', 'node-title', order === 1 ? '#1 · next' : `#${order}`));
        item.appendChild(miniBoard(e.board, true));
        item.appendChild(costBadges(e.g, e.h, e.f));
        fr.appendChild(item);
      });
      d.appendChild(fr);
    }

    traceBodyEl.appendChild(d);
  });

  if (trace.truncated) {
    traceBodyEl.appendChild(makeEl('div', 'muted', `Trace limited to the first ${trace.steps.length} steps.`));
  }
  traceNoteEl.textContent = `(${trace.steps.length} steps)`;
}

// solve button click
async function handleSolve() {
  const initial = parseInputState();
  if (!initial) return;

  clearSolution();
  currentBoard = initial;
  renderBoard(currentBoard);

  const algorithm = document.getElementById('algorithm-select').value;
  btnSolve.disabled = true;

  try {
    const res = await fetch('/solve', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        initial_state: initial,
        algorithm: algorithm
      })
    });

    const data = await res.json();
    btnSolve.disabled = false;

    if (!data.success) {
      if (data.error === "no solution found" || data.error.includes("could not find a solution")) {
        const defaultSample = [1, 2, 5, 3, 4, 0, 6, 7, 8];
        const isDefault = initial.every((val, i) => val === defaultSample[i]);
        if (isDefault) {
          showAlert('backend algorithms are stubs — previewing sample path for default board', 'success');
          loadDemoPreview(initial);
          return;
        } else {
          showAlert('algorithm returned no solution (implement algorithms in solver/ to solve random boards)', 'error');
          return;
        }
      }
      showAlert(data.error || 'could not solve puzzle', 'error');
      return;
    }

    solutionPath = data.path;
    solutionMoves = data.moves || [];
    currentStep = 0;

    statMovesEl.textContent = solutionMoves.join(', ') || 'None';
    statCostEl.textContent = data.cost ?? solutionPath.length - 1;
    statNodesEl.textContent = data.nodes_expanded ? data.nodes_expanded.toLocaleString() : '—';
    statDepthEl.textContent = data.search_depth ?? data.cost ?? '—';
    statTimeEl.textContent = data.running_time !== undefined ? `${Number(data.running_time).toFixed(4)}s` : '—';

    renderPathList();
    updatePlaybackUI();
    showAlert(`solution found (${solutionPath.length - 1} moves)`, 'success');
    play();
    renderTrace(data.trace);

  } catch (err) {
    btnSolve.disabled = false;
    showAlert('server connection error — previewing sample path', 'error');
    loadDemoPreview(initial);
  }
}

// valid sequence of strictly adjacent moves from [1,2,5,3,4,0,6,7,8] to goal
function loadDemoPreview(startBoard) {
  // move 1: blank moves Up (swaps with 5)
  // move 2: blank moves Left (swaps with 2)
  // move 3: blank moves Left (swaps with 1) -> goal reached!
  solutionPath = [
    [1, 2, 5, 3, 4, 0, 6, 7, 8],
    [1, 2, 0, 3, 4, 5, 6, 7, 8],
    [1, 0, 2, 3, 4, 5, 6, 7, 8],
    [0, 1, 2, 3, 4, 5, 6, 7, 8]
  ];
  solutionMoves = ['Up', 'Left', 'Left'];
  currentStep = 0;

  statMovesEl.textContent = solutionMoves.join(', ');
  statCostEl.textContent = '3';
  statNodesEl.textContent = '14';
  statDepthEl.textContent = '3';
  statTimeEl.textContent = '0.0015s';

  renderPathList();
  updatePlaybackUI();
  play();
}

function showAlert(msg, type) {
  alertBoxEl.textContent = msg;
  alertBoxEl.className = `alert ${type}`;
}

function hideAlert() {
  alertBoxEl.className = 'alert hidden';
}

// event listeners
btnSolve.addEventListener('click', handleSolve);
btnReset.addEventListener('click', () => {
  const initial = parseInputState();
  if (initial) {
    clearSolution();
    currentBoard = initial;
    renderBoard(currentBoard);
  }
});

btnRandom.addEventListener('click', generateRandomSolvable);
btnPlay.addEventListener('click', togglePlay);
btnPrev.addEventListener('click', () => {
  pause();
  goToStep(currentStep - 1);
});
btnNext.addEventListener('click', () => {
  pause();
  goToStep(currentStep + 1);
});

inputEl.addEventListener('change', () => {
  const parsed = parseInputState();
  if (parsed) {
    currentBoard = parsed;
    renderBoard(currentBoard);
    clearSolution();
  }
});

// initial render
renderBoard(currentBoard);
clearSolution();
