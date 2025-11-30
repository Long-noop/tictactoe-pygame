# GamePlaying - TicTacToe

# I. Tìm hiểu

## 1. Mục tiêu

• Hiện thực game playing agent cho một trò chơi tự chọn (dạng đối kháng).

• Nâng cao kỹ năng lập trình, giải quyết vấn đề.

## 2. Yêu cầu

Mỗi nhóm chọn một trò chơi không dễ - trò chơi nếu sinh cây phải có hệ số nhánh cao và độ sâu
của cây từ 30 trở lên (VD: cờ tướng, cờ vua, cờ vây, ...) để hiện thực bằng giải thuật Minimax và
giải thuật – mô hình Học máy (bất kỳ), với yêu cầu cụ thể như sau:

1. Agent phải chơi đúng luật.
2. Minimax thắng được agent chơi ngẫu nhiên với tỉ lệ 90%.
3. Học máy thắng được agent chơi ngẫu nhiên với tỉ lệ 60%.
4. Nhóm tạo video thuyết trình (tối đa 15 phút) về trò chơi, hiện thực của nhóm, và kết quả
của các giải thuật.

Đề bài nêu rõ có **3 loại agent khác nhau** mà nhóm phải hiện thực:

| Loại Agent | Mô tả | Vai trò trong bài |
| --- | --- | --- |
| 🎲 **Random Agent** | Chơi ngẫu nhiên — chọn bất kỳ nước hợp lệ nào (legal move) một cách random. | Là đối thủ kiểm thử (benchmark) để đo hiệu quả. |
| 🧠 **Minimax Agent** | Agent dùng thuật toán **Minimax (hoặc Alpha-Beta pruning)** để chọn nước tối ưu dựa trên mô phỏng cây trạng thái. | Phải thắng Random Agent ≥ **90%**. |
| 🤖 **Learning Agent** | Agent dùng **một mô hình học máy** (VD: Q-learning, Neural Network, Decision Tree, v.v.) để tự học cách chơi. | Phải thắng Random Agent ≥ **60%**. |

### DEMO with Random Agent

[GitHub - Long-noop/tictactoe-pygame: A well known two player game made using Python and Pygame.](https://github.com/Long-noop/tictactoe-pygame)

### **Agent Classes**

Có thể thiết kế như sau:

```python
class Agent:
    def __init__(self, symbol):
        self.symbol = symbol  # 'X' hoặc 'O'
    def get_move(self, state):
        pass  # được override ở từng loại agent
```

Rồi kế thừa:

```python
class RandomAgent(Agent):
    def get_move(self, state):
        moves = get_legal_moves(state)
        return random.choice(moves)
```

```python
class MinimaxAgent(Agent):
    def get_move(self, state):
        best_move = minimax(state, depth, alpha, beta, True)
        return best_move
```

```python
class LearningAgent(Agent):
    def get_move(self, state):
        # Dựa vào model học máy đã train
        return model.predict_best_move(state)
```

---

## 3. Xác định quy tắc cơ bản

- Bàn cờ: 9 **× 9 = 81 ô.**
- Mỗi lượt: người chơi đặt 1 dấu (X hoặc O) vào **1 ô trống**.
- Điều kiện thắng (thông thường trong bản mở rộng): 5 **liên tiếp** (ngang, dọc, chéo).
- Không có ăn quân hay loại bỏ quân (tức là không có “back-move”).

---

### Độ sâu tối đa (max depth)

**Độ sâu cây tìm kiếm = số nước đi tối đa trong một ván.**

- Ở Tic-Tac-Toe 9×9: tổng cộng 81 **ô**,
- Mỗi lượt đi chiếm 1 ô,
    
    → Nếu không ai thắng sớm, thì **max depth = 81.**
    

`maxDepth = 81` (trong trường hợp ván kéo dài đến hết bàn).

---

### Branching Factor (hệ số nhánh)

a. Định nghĩa:

Hệ số nhánh trung bình (average branching factor, ký hiệu *b*) là **số lượng nước đi hợp lệ trung bình tại mỗi trạng thái**.

b. Phân tích:

- Ban đầu: có 81 nước đi hợp lệ.
- Sau 1 nước: còn 80, rồi 79, … cho đến 1.
- Trung bình ta có thể xấp xỉ:  $b = (81+1)/2=41$
    
    41 **nước đi hợp lệ trung bình mỗi lượt**.
    

> ✅ Kết luận:
> 
> 
> `Branching factor ≈ 41`
> 
> `Max depth = 81`
> 

---

### So sánh với các phiên bản khác

| Phiên bản | Ô | Branching Factor (≈) | Max Depth | Nhận xét |
| --- | --- | --- | --- | --- |
| 3×3 | 9 | 4.5 | 9 | Quá nhỏ, dễ giải hết cây |
| 4×4 | 16 | 8 | 16 | Trung bình |
| 5×5 | 25 | 12.5 | 25 | Trung bình |
| **6×6** | **36** | **18** | **36** | ✅ **Đạt yêu cầu đề bài (độ sâu ≥ 30, hệ số nhánh cao)** |

---

# II. MiniMax Agent

## 4. Giải thuật Minimax

Nếu ta dùng Minimax **không pruning**, số trạng thái cần duyệt sẽ là: $41^{81}$ (rất lớn, không thể tính hết)

→ Vì vậy **bắt buộc** phải dùng **alpha-beta pruning** + **giới hạn độ sâu (depth limit)**, ví dụ:

- Depth limit = 5 hoặc 6.
- Evaluation function (heuristic) đánh giá tạm thời.

---

### Ý tưởng tổng quát

**Minimax** giúp agent chọn nước đi tối ưu, giả định rằng:

- Agent (X) luôn **cố gắng tối đa hóa** điểm (maximize).
- Đối thủ (O) luôn **cố gắng tối thiểu hóa** điểm (minimize).

Cây trò chơi được sinh ra bởi các trạng thái bàn cờ → nước đi hợp lệ → trạng thái mới.

### Alpha–Beta pruning

Dùng để **cắt bỏ nhánh không cần thiết**:

- `α` = giá trị tốt nhất (max) mà **người chơi MAX** có thể đảm bảo.
- `β` = giá trị tốt nhất (min) mà **người chơi MIN** có thể đảm bảo.

Nếu tại bất kỳ điểm nào `α ≥ β`, ta **cắt bỏ (prune)** nhánh còn lại.

---

## 5. Định nghĩa không gian trạng thái (State Space Definition)

### 5.1.  Cấu trúc state:

Một state gồm:

```python
class GameState:
    def __init__(self, board, current_player):
        self.board = board          # ma trận 9x9
        self.current_player = current_player  # 'X' hoặc 'O'

```

### Không gian trạng thái:

Là **tập hợp tất cả các trạng thái hợp lệ** có thể sinh ra từ state ban đầu theo luật chơi:

[

S = { s0, s1, s2, …, sn }

]

Trong đó:

- `s_0`: trạng thái ban đầu (initial state)
- `s_n`: trạng thái kết thúc (terminal state)
- `s_{i+1}` được sinh ra từ `s_i` bằng một nước đi hợp lệ (legal move).

---

### 5.2. Initial state (trạng thái ban đầu)

```python
def initial_state():
    board = [["." for _ in range(6)] for _ in range(6)]
    return GameState(board, current_player="X")

```

---

### 5.3. Terminal state (trạng thái kết thúc)

Một trạng thái là **terminal** nếu:

- Một người chơi thắng (có 4 liên tiếp), hoặc
- Không còn ô trống (hòa).

```python
def is_terminal(state):
    return check_winner(state.board, "X") or check_winner(state.board, "O") \
           or all(cell != "." for row in state.board for cell in row)

```

---

### 5.4. Legal moves (các hành động hợp lệ)

Các nước đi hợp lệ là **các ô trống** còn lại trên bàn:

```python
def get_legal_moves(state):
    return [(r, c) for r in range(6) for c in range(6) if state.board[r][c] == "."]

```

---

### 5.5. Transition model (mô hình chuyển trạng thái)

Áp dụng một hành động `move = (r, c)` vào state → sinh ra state mới:

```python
def result(state, move):
    r, c = move
    new_board = [row[:] for row in state.board]
    new_board[r][c] = state.current_player
    next_player = "O" if state.current_player == "X" else "X"
    return GameState(new_board, next_player)

```

---

### 5.6. Evaluation Function (Đánh giá trạng thái)

Hàm này ước lượng **độ tốt** của một trạng thái *khi chưa kết thúc game*, dùng để:

- So sánh các trạng thái.
- Alpha–Beta pruning.

Mục tiêu:

- Giá trị càng cao → càng có lợi cho người chơi X.
- Giá trị càng thấp → càng có lợi cho người chơi O.

---

5.6.1 Phương pháp cơ bản: “Đếm chuỗi liên tiếp”

Với bàn 9x9 và luật 5-in-a-row, ta xem:

| Thành phần | Mô tả | Gợi ý trọng số |
| --- | --- | --- |
| `open_fours` | Số lượng chuỗi 4 quân liên tiếp có 2 đầu mở | +1000 |
| `open_threes` | Số lượng chuỗi 3 quân liên tiếp có 2 đầu mở | +100 |
| `blocked_fours` | Chuỗi 4 quân bị chặn 1 đầu | +300 |
| `two_in_row` | Cặp quân liên tiếp | +10 |

Tương tự cho đối thủ → trừ điểm.

---

5.6.2. Cài đặt hàm đánh giá 

```python
# Mã tham khảo áp dụng cho map 6x6, sửa lại theo đúng yêu cầu map 9x9

def evaluate_line(line, player):
    opp = "O" if player == "X" else "X"
    score = 0
    if opp not in line:
        count = line.count(player)
        if count == 2:
            score += 10
        elif count == 3:
            score += 50
        elif count >= 4:
            score += 1000
    return score

def evaluate_state(state, player="X"):
    board = state.board
    total_score = 0

    # hàng ngang
    for r in range(6):
        for c in range(6 - 4 + 1):
            line = [board[r][c + i] for i in range(4)]
            total_score += evaluate_line(line, player)
            total_score -= evaluate_line(line, "O" if player == "X" else "X")

    # hàng dọc
    for c in range(6):
        for r in range(6 - 4 + 1):
            line = [board[r + i][c] for i in range(4)]
            total_score += evaluate_line(line, player)
            total_score -= evaluate_line(line, "O" if player == "X" else "X")

    # chéo xuôi & ngược
    for r in range(6 - 4 + 1):
        for c in range(6 - 4 + 1):
            diag1 = [board[r + i][c + i] for i in range(4)]
            diag2 = [board[r + 3 - i][c + i] for i in range(4)]
            total_score += evaluate_line(diag1, player)
            total_score -= evaluate_line(diag1, "O" if player == "X" else "X")
            total_score += evaluate_line(diag2, player)
            total_score -= evaluate_line(diag2, "O" if player == "X" else "X")

    return total_score

```

---

Tổng quan mối quan hệ giữa các thành phần

| Thành phần | Hàm / Lớp tương ứng | Vai trò |
| --- | --- | --- |
| **State** | `GameState` | Mô tả tình trạng hiện tại |
| **Initial state** | `initial_state()` | Bắt đầu game |
| **Legal moves** | `get_legal_moves(state)` | Sinh hành động hợp lệ |
| **Transition** | `result(state, move)` | Sinh state con |
| **Terminal** | `is_terminal(state)` | Kiểm tra kết thúc |
| **Evaluation** | `evaluate_state(state)` | Ước lượng độ tốt của state |

---

## 6. Cách tích hợp vào Minimax

Sau khi có tất cả các thành phần trên, ta triển khai:

```python
def minimax(state, depth, alpha, beta, maximizing_player, root_player):
    if is_terminal(state) or depth == 0:
        return evaluate_state(state, root_player)

    if maximizing_player:
        max_eval = -float("inf")
        for move in get_legal_moves(state):
            eval = minimax(result(state, move), depth-1, alpha, beta, False, root_player)
            max_eval = max(max_eval, eval)
            alpha = max(alpha, eval)
            if beta <= alpha:
                break  # pruning
        return max_eval
    else:
        min_eval = float("inf")
        for move in get_legal_moves(state):
            eval = minimax(result(state, move), depth-1, alpha, beta, True, root_player)
            min_eval = min(min_eval, eval)
            beta = min(beta, eval)
            if beta <= alpha:
                break
        return min_eval

```

---

# III. ML Agent

## Các hướng ML khả thi

Có **3 hướng chính**, tùy độ phức tạp muốn triển khai:

| Cấp độ | Phương pháp | Mô tả | Ưu điểm |
| --- | --- | --- | --- |
| **Cơ bản**  | **Q-learning (Reinforcement Learning)** | Agent tự học qua thử-sai, cập nhật bảng giá trị Q(s, a). | Dễ hiểu, không cần dữ liệu sẵn. |
| **Trung bình** | **Supervised Learning (Học có giám sát)** | Train mô hình (MLP, SVM, Decision Tree, v.v.) dự đoán nước đi tốt nhất dựa trên dữ liệu từ Minimax hoặc chuyên gia. | Tận dụng dữ liệu, dễ kiểm soát. |
| **Nâng cao** | **Deep Reinforcement Learning** | Dùng Neural Network làm hàm Q hoặc Policy (như AlphaZero). | Cực mạnh, nhưng phức tạp. |

## 1. Q-Learning

[Q-Learning in Reinforcement Learning - GeeksforGeeks](https://www.geeksforgeeks.org/machine-learning/q-learning-in-python/)

### 1.1 Q-Learning cơ bản

### a. Khái niệm

Q-learning học hàm giá trị:

$Q(s,a)=$ giá trị  kỳ vọng nếu thực hiện hành động a trong trạng thái s

### b. Cập nhật Q

Sau mỗi lượt đi:

$Q(s, a) = R(s, a) + γ * max_a' Q(s', a')$

Trong đó:

- `α` = learning rate
- `γ` = discount factor
- `r` = reward (thưởng/phạt)
- `s'` = trạng thái sau khi đi nước `a`

---

### 1.2 Quy trình học

1. **Khởi tạo:**
    
    ```python
    Q = {}  # dictionary lưu giá trị Q[(state, move)]
    ```
    
2. **Chạy nhiều ván huấn luyện:**
    - Agent chơi với random agent hoặc self-play.
    - Sau mỗi lượt: cập nhật `Q(s, a)`.
3. **Reward:**
    
    
    | Tình huống | Reward |
    | --- | --- |
    | Thắng | +1 |
    | Thua | -1 |
    | Hòa | 0 |
    | Nước đi hợp lệ trung gian | 0 |
4. **Chọn hành động (Exploration/Exploitation):**
    
    ```python
    if random() < epsilon:
        move = random.choice(legal_moves)
    else:
        move = argmax(Q[state, move])
    ```
    
5. **Sau khi học đủ số ván**, giảm `epsilon` → agent bắt đầu **chơi “thông minh” hơn**.

---

1. Ví dụ code khung (Python)

```python
import random
from collections import defaultdict

Q = defaultdict(float)
alpha = 0.1
gamma = 0.9
epsilon = 0.2

def choose_action(state, legal_moves):
    if random.random() < epsilon:
        return random.choice(legal_moves)
    else:
        q_values = [Q[(state, move)] for move in legal_moves]
        return legal_moves[q_values.index(max(q_values))]

def update_Q(state, action, reward, next_state, next_legal_moves):
    next_q = max([Q[(next_state, a)] for a in next_legal_moves], default=0)
    Q[(state, action)] += alpha * (reward + gamma * next_q - Q[(state, action)])

```

---

### 1.3 Đánh giá trạng thái (state representation)

Vì bàn Tic-Tac-Toe 9×9 khá lớn, ta cần **biểu diễn trạng thái đơn giản**:

- Encode bàn cờ thành chuỗi: `"XOXO....O"` (81 ký tự)
- Hoặc tuple: `('X', 'O', ' ', 'X', ...)`
- Có thể mã hóa `X = 1, O = -1, trống = 0`.

## Supervised Learning

[Supervised and Unsupervised learning - GeeksforGeeks](https://www.geeksforgeeks.org/machine-learning/supervised-unsupervised-learning/)

Nếu có thời gian:

- Dùng **dữ liệu Minimax** (với depth nhỏ) để tạo dataset:
    
    `input = state`, `label = best_move`.
    
- Train model đơn giản (MLP hoặc DecisionTreeClassifier) để học cách bắt chước Minimax.
- Sau đó để agent dùng model này để chọn nước đi.

## **Phân chia công việc (deadline nộp thầy 12/12/2025)**

| Task | Thành viên | Nhiệm vụ chính | Mục tiêu | Deadline |
| --- | --- | --- | --- | --- |
| **1. Random Agent (đã xong)** | Long | - Sinh nước đi hợp lệ ngẫu nhiên, đảm bảo luật chơi
- Viết **giao diện mô phỏng game (UI / CLI)** | Là baseline để test Minimax & ML | Trước deadline thực 10 ngày để làm báo cáo + present
(2/12/2025) |
| **2. Minimax Agent (1 người)** | Hân | - Xây dựng **không gian trạng thái** (state space) 
- Hiện thực **Minimax + Alpha-Beta pruning**
 - Tối ưu hiệu suất sinh nước đi 
- Xây dựng **hàm đánh giá (heuristic)** | Minimax thắng random ≥ 90% | Trước deadline thực 10 ngày để làm báo cáo + present
(2/12/2025) |
| **3. Machine Learning Agent (1 người)** | Thanh | - Thu thập dataset (từ Minimax vs Random hoặc từ log nếu chọn ML là Supervised  Learning)
 - Thiết kế **feature vector** cho trạng thái game 
- Huấn luyện model (supervised learning hoặc reinforcement learning)
 - Tích hợp vào agent để chọn nước đi | ML thắng random ≥ 60% | Trước deadline thực 10 ngày để làm báo cáo + present
(2/12/2025) |
| **4. Documentation & Presentation (2 người)
- 1 người làm report
- 1 người làm slide + present video** | **- slide + present : Lộc

- report : Quang** | - Tổng hợp tài liệu kỹ thuật 
- Viết **report** & **slide**
- Chuẩn bị **video thuyết trình 15 phút** 
 | Báo cáo + trình bày |  |
| **5. Integration & Testing(1 người)** | Long | - Chạy **test tự động** với Random Agent 
- Ghi log kết quả để dùng cho ML 
- Tối ưu performance
- Thống kê tỉ lệ thắng, biểu đồ kết quả | Đảm bảo 3 agent tương tác đúng & chạy mượt | Trước deadline thực 10 ngày để làm báo cáo + present
(2/12/2025) |

**NOTE: Trong quá trình hiện thực các agent,  ghi lại quá trình hiện thực và kiểm thử để phục vụ viết báo cáo**