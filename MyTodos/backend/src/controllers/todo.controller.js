import Todo from "../models/Todo.js";

export const createTodo = async (req, res) => {
  try {
    const todo = await Todo.create({ text: req.body.text });
    res.json(todo);
  } catch (err) {
    res.status(500).json({ error: "Error creating todo" });
  }
};

export const getTodos = async (req, res) => {
  try {
    const todos = await Todo.find();
    res.json(todos);
  } catch (err) {
    res.status(500).json({ error: "Error fetching todos" });
  }
};

export const toggleTodo = async (req, res) => {
  try {
    const todo = await Todo.findById(req.params.id);

    todo.completed = !todo.completed;
    await todo.save();

    res.json(todo);
  } catch (err) {
    res.status(500).json({ error: "Cannot toggle todo" });
  }
};

export const deleteTodo = async (req, res) => {
  try {
    await Todo.findByIdAndDelete(req.params.id);
    res.json({ message: "Deleted" });
  } catch (err) {
    res.status(500).json({ error: "Cannot delete todo" });
  }
};

export const updateTodo = async (req, res) => {
  try {
    const todo = await Todo.findById(req.params.id);
    todo.text = req.body.text;
    await todo.save();
    res.json(todo);
  } catch (err) {
    res.status(500).json({ error: "Cannot update todo" });
  }
};