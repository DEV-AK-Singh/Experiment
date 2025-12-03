import type { Todo } from "../types/Todo.ts";

const BASE_URL = import.meta.env.VITE_API_URL + "/todos";

export const getTodos = async (): Promise<Todo[]> => {
  const res = await fetch(BASE_URL);
  return res.json();
};

export const addTodo = async (text: string): Promise<Todo> => {
  const res = await fetch(BASE_URL, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ text }),
  });
  return res.json();
};

export const toggleTodo = async (id: string): Promise<Todo> => {
  const res = await fetch(`${BASE_URL}/${id}`, { method: "PUT" });
  return res.json();
};

export const deleteTodo = async (id: string): Promise<{ message: string }> => {
  const res = await fetch(`${BASE_URL}/${id}`, { method: "DELETE" });
  return res.json();
};

export const updateTodo = async (
  id: string,
  text: string,
): Promise<Todo> => {
  const res = await fetch(`${BASE_URL}/${id}`, {
    method: "PATCH",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ text }),
  });
  return res.json();
};