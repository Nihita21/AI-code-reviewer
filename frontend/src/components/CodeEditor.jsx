import Editor from "@monaco-editor/react";

function CodeEditor() {
  return (
    <Editor
      height="500px"
      defaultLanguage="python"
      defaultValue="# Write your code here..."
      theme="vs-dark"
    />
  );
}

export default CodeEditor;