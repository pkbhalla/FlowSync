// flowsync/static/js/kanban.js

document.addEventListener('DOMContentLoaded', () => {
    const board = document.querySelector('.kanban-board');
    if (!board) return;

    const tasks = document.querySelectorAll('.task-card');
    const columns = document.querySelectorAll('.kanban-col-body');

    let draggedTask = null;

    tasks.forEach(task => {
        task.addEventListener('dragstart', (e) => {
            draggedTask = task;
            setTimeout(() => task.classList.add('dragging'), 0);
        });

        task.addEventListener('dragend', () => {
            draggedTask.classList.remove('dragging');
            draggedTask = null;
        });
    });

    columns.forEach(col => {
        col.addEventListener('dragover', (e) => {
            e.preventDefault();
            const afterElement = getDragAfterElement(col, e.clientY);
            if (afterElement == null) {
                col.appendChild(draggedTask);
            } else {
                col.insertBefore(draggedTask, afterElement);
            }
        });

        col.addEventListener('drop', async (e) => {
            e.preventDefault();
            if (!draggedTask) return;
            
            const newStatus = col.closest('.kanban-col').getAttribute('data-status');
            const taskId = draggedTask.getAttribute('data-task-id');
            const oldStatus = draggedTask.getAttribute('data-status');

            if (newStatus !== oldStatus) {
                draggedTask.setAttribute('data-status', newStatus);
                try {
                    // Update server
                    await window.apiFetch(`/tasks/${taskId}/update-status`, {
                        method: 'POST',
                        body: JSON.stringify({ status: newStatus })
                    });
                    window.showToast('Task status updated');
                } catch (err) {
                    // Revert on failure
                    draggedTask.setAttribute('data-status', oldStatus);
                    const oldCol = document.querySelector(`.kanban-col[data-status="${oldStatus}"] .kanban-col-body`);
                    if(oldCol) oldCol.appendChild(draggedTask);
                }
            }
        });
    });

    function getDragAfterElement(container, y) {
        const draggableElements = [...container.querySelectorAll('.task-card:not(.dragging)')];
        return draggableElements.reduce((closest, child) => {
            const box = child.getBoundingClientRect();
            const offset = y - box.top - box.height / 2;
            if (offset < 0 && offset > closest.offset) {
                return { offset: offset, element: child };
            } else {
                return closest;
            }
        }, { offset: Number.NEGATIVE_INFINITY }).element;
    }

    // Client side filtering
    const filterSelect = document.getElementById('task-filter');
    if (filterSelect) {
        filterSelect.addEventListener('change', (e) => {
            const val = e.target.value;
            const currentUserId = document.body.getAttribute('data-user-id');
            tasks.forEach(t => {
                if (val === 'all') t.style.display = 'block';
                else if (val === 'my_tasks' && t.getAttribute('data-assignee') === currentUserId) t.style.display = 'block';
                else if (val === 'high_priority' && t.getAttribute('data-priority') === 'high') t.style.display = 'block';
                else if (val === 'overdue' && t.getAttribute('data-overdue') === 'true') t.style.display = 'block';
                else t.style.display = 'none';
            });
        });
    }
});
