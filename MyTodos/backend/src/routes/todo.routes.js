import express from "express";
import { createTodo, getTodos, toggleTodo, deleteTodo, updateTodo } from "../controllers/todo.controller.js";

const router = express.Router();

router.post("/", createTodo);
router.get("/", getTodos);
router.put("/:id", toggleTodo);
router.delete("/:id", deleteTodo);
router.patch("/:id", updateTodo);

export default router;
