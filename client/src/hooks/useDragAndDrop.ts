import { useState, useCallback } from 'react';

interface UseDragAndDropProps {
  onFileDrop: (file: File) => void;
  onDragStart?: () => void;
  onDragEnd?: () => void;
}

interface UseDragAndDropResult {
  isDragActive: boolean;
  dragHandlers: {
    onDragOver: (e: React.DragEvent) => void;
    onDragLeave: (e: React.DragEvent) => void;
    onDrop: (e: React.DragEvent) => void;
  };
  keyboardHandlers: {
    onKeyDown: (e: React.KeyboardEvent) => void;
  };
}

/**
 * Hook to manage drag and drop interactions for file uploads
 * Provides handlers and state for drag operations
 */
export const useDragAndDrop = ({ 
  onFileDrop, 
  onDragStart, 
  onDragEnd 
}: UseDragAndDropProps): UseDragAndDropResult => {
  const [isDragActive, setIsDragActive] = useState(false);

  const onDragOver = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    setIsDragActive(true);
    onDragStart?.();
  }, [onDragStart]);

  const onDragLeave = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    setIsDragActive(false);
    onDragEnd?.();
  }, [onDragEnd]);

  const onDrop = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    setIsDragActive(false);
    onDragEnd?.();
    
    const files = e.dataTransfer.files;
    if (files.length > 0) {
      onFileDrop(files[0]);
    }
  }, [onFileDrop, onDragEnd]);

  const onKeyDown = useCallback((e: React.KeyboardEvent) => {
    if (e.key === 'Enter' || e.key === ' ') {
      e.preventDefault();
      e.stopPropagation();
      // Let the component handle the click with inputRef
    }
  }, []);

  return {
    isDragActive,
    dragHandlers: {
      onDragOver,
      onDragLeave,
      onDrop,
    },
    keyboardHandlers: {
      onKeyDown,
    },
  };
};