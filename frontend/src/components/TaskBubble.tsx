import React from 'react';

interface TaskBubbleProps {
  task: {
    name: string;
    icon: React.ReactNode;
  };
  isSelected: boolean;
  onClick: () => void;
}

export const TaskBubble: React.FC<TaskBubbleProps> = ({ task, isSelected, onClick }) => {
  return (
    <button
      onClick={onClick}
      className={`flex items-center space-x-2 p-2 rounded-full transition-colors ${
        isSelected
          ? 'bg-primary text-primary-foreground'
          : 'bg-secondary text-secondary-foreground hover:bg-secondary/80'
      }`}
    >
      {task.icon && <span className="w-4 h-4">{task.icon}</span>}
      <span className="text-sm font-medium">{task.name}</span>
    </button>
  );
};