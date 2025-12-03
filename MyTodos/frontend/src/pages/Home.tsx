import { useEffect, useState } from "react";
import type { Todo } from "../types/Todo";
import { getTodos, addTodo, toggleTodo, deleteTodo, updateTodo } from "../api/todoApi";
import TodoItem from "../components/TodoItem";

export default function Home() {
  const [todos, setTodos] = useState<Todo[]>([]);
  const [text, setText] = useState<string>("");

  const load = async () => {
    const data = await getTodos();
    setTodos(data);
  };

  const add = async () => {
    if (text.trim() === "") return;
    await addTodo(text);
    setText("");
    load();
  };  

  useEffect(() => {
    load();
  }, []);

  return (
    <div style={{ padding: 20 }}>
      <h1>My Todos</h1>

      <input
        value={text}
        onChange={(e) => setText(e.target.value)}
        placeholder="Enter todo"
      />
      <button onClick={add}>Add</button>

      <div style={{ marginTop: 20 }}>
        {todos.map((todo) => (
          <TodoItem
            key={todo._id}
            todo={todo}
            onToggle={() => toggleTodo(todo._id).then(load)}
            onDelete={() => deleteTodo(todo._id).then(load)}
            onUpdate={(text: string) => updateTodo(todo._id, text).then(load)}
          />
        ))}
      </div>
    </div>
  );
}
