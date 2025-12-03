import express from "express";
import cors from "cors";
import dotenv from "dotenv";

import todoRoutes from "./routes/todo.routes.js";

dotenv.config();

const app = express();
app.use(cors());
app.use(express.json());

app.use("/api/todos", todoRoutes);

export default app;
