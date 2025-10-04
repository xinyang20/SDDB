const rowsPerPage = 5;
const rows = document.querySelectorAll(".task-row");
const pagination = document.getElementById("pagination");

function displayPage(page) {
  const start = (page - 1) * rowsPerPage;
  const end = start + rowsPerPage;

  rows.forEach((row, index) => {
    row.style.display = index >= start && index < end ? "" : "none";
  });
}

function setupPagination() {
  const totalPages = Math.ceil(rows.length / rowsPerPage);
  pagination.innerHTML = "";

  for (let i = 1; i <= totalPages; i++) {
    const button = document.createElement("button");
    button.textContent = i;
    button.className = i === 1 ? "active" : "";
    button.addEventListener("click", () => {
      document
        .querySelector(".pagination button.active")
        .classList.remove("active");
      button.classList.add("active");
      displayPage(i);
    });
    pagination.appendChild(button);
  }
}

displayPage(1);
setupPagination();

function openRollbackModal(button) {
  const taskId = button.getAttribute("data-task-id");
  const receiveCompleted =
    button.getAttribute("data-receive-completed") === "true";
  const formCompleted = button.getAttribute("data-form-completed") === "true";
  const decoctionStarted =
    button.getAttribute("data-decoction-started") === "true";
  const decoctionEnded = button.getAttribute("data-decoction-ended") === "true";

  document.getElementById("rollbackModal").style.display = "block";
  document.getElementById("rollbackTaskId").value = taskId;

  const rollbackPhase = document.getElementById("rollback_phase");
  rollbackPhase.innerHTML = "";

  if (decoctionEnded) {
    rollbackPhase.innerHTML +=
      '<option value="decoction_end">煎药结束</option>';
  }
  if (decoctionStarted) {
    rollbackPhase.innerHTML +=
      '<option value="decoction_start">煎药开始</option>';
  }
  if (formCompleted) {
    rollbackPhase.innerHTML += '<option value="formulate">配方</option>';
  }
  if (receiveCompleted) {
    rollbackPhase.innerHTML += '<option value="receive">收方</option>';
  }

  if (rollbackPhase.innerHTML === "") {
    rollbackPhase.innerHTML = "<option disabled>无可回退阶段</option>";
  }
}

function closeRollbackModal() {
  document.getElementById("rollbackModal").style.display = "none";
}

// 监听表单提交 - 使用事件委托确保动态加载的表单也能被捕获
document.addEventListener("DOMContentLoaded", function () {
  document.addEventListener("submit", async (e) => {
    // 检查是否是任务分配相关的表单
    if (e.target.matches('form[action*="assign_tasks"]')) {
      e.preventDefault(); // 阻止默认提交

      const form = e.target;
      const formData = new FormData(form);

      try {
        const response = await fetch(form.action, {
          method: "POST",
          body: formData,
        });

        const data = await response.json(); // 解析返回的 JSON 数据

        if (data.success) {
          // 成功提示
          alert(data.message);
          location.reload(); // 刷新页面，显示新的分配状态
        } else {
          // 错误提示
          alert(data.message);
        }
      } catch (error) {
        console.error("Error:", error);
        alert("操作失败，请重试");
      }
    }
  });
});
