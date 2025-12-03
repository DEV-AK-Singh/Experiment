import { useState } from "react";
import type { Todo } from "../types/Todo";

interface Props {
  todo: Todo;
  onToggle: () => void;
  onDelete: () => void;
  onUpdate: (text: string) => void;
}

export default function TodoItem({
  todo,
  onToggle,
  onDelete,
  onUpdate,
}: Props) {
  const [text, setText] = useState<string>(todo.text); 
  return (
    <div className="todo">
      <input type="checkbox" checked={todo.completed} onChange={onToggle} />
      <span
        style={{
          textDecoration: todo.completed ? "line-through" : "none",
        }} 
        onInput={(e) => {
          setText(e.currentTarget.textContent || "");
        }}
        onKeyDown={(e) => {
          if (e.key === "Enter") {
            onUpdate(text); 
            e.currentTarget.blur();
          }
        }}
        contentEditable
        suppressContentEditableWarning={true}
      >
        {todo.text}
      </span>
      <button onClick={onDelete}>❌</button>
    </div>
  );
}
