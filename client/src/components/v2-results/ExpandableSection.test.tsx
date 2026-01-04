/**
 * Tests for ExpandableSection component
 */

import React from 'react';
import { render, screen, fireEvent } from '@testing-library/react';
import { ChevronDown } from 'lucide-react';
import { ExpandableSection, ExpandableSectionList } from './ExpandableSection';

describe('ExpandableSection', () => {
  const testProps = {
    title: 'Test Section',
    children: <div>Test Content</div>
  };

  it('should render with title', () => {
    render(<ExpandableSection {...testProps} />);
    expect(screen.getByText('Test Section')).toBeInTheDocument();
  });

  it('should render description if provided', () => {
    render(
      <ExpandableSection
        {...testProps}
        description="Test description"
      />
    );
    expect(screen.getByText('Test description')).toBeInTheDocument();
  });

  it('should start collapsed by default', () => {
    render(<ExpandableSection {...testProps} />);
    expect(screen.queryByText('Test Content')).not.toBeInTheDocument();
  });

  it('should start expanded if defaultExpanded is true', () => {
    render(
      <ExpandableSection
        {...testProps}
        defaultExpanded={true}
      />
    );
    expect(screen.getByText('Test Content')).toBeInTheDocument();
  });

  it('should expand on header click', () => {
    render(<ExpandableSection {...testProps} />);
    const header = screen.getByText('Test Section').closest('button');
    
    fireEvent.click(header!);
    expect(screen.getByText('Test Content')).toBeInTheDocument();
  });

  it('should collapse on second header click', () => {
    render(
      <ExpandableSection
        {...testProps}
        defaultExpanded={true}
      />
    );
    const header = screen.getByText('Test Section').closest('button');
    
    fireEvent.click(header!);
    expect(screen.queryByText('Test Content')).not.toBeInTheDocument();
  });

  it('should render icon if provided', () => {
    render(
      <ExpandableSection
        {...testProps}
        icon={<ChevronDown className="w-5 h-5" data-testid="icon" />}
      />
    );
    expect(screen.getByTestId('icon')).toBeInTheDocument();
  });

  it('should apply custom className', () => {
    const { container } = render(
      <ExpandableSection
        {...testProps}
        className="custom-class"
      />
    );
    expect(container.querySelector('.custom-class')).toBeInTheDocument();
  });
});

describe('ExpandableSectionList', () => {
  const testSections = [
    {
      title: 'Section 1',
      content: <div>Content 1</div>
    },
    {
      title: 'Section 2',
      description: 'Description 2',
      content: <div>Content 2</div>
    }
  ];

  it('should render all sections', () => {
    render(<ExpandableSectionList sections={testSections} />);
    expect(screen.getByText('Section 1')).toBeInTheDocument();
    expect(screen.getByText('Section 2')).toBeInTheDocument();
  });

  it('should render descriptions if provided', () => {
    render(<ExpandableSectionList sections={testSections} />);
    expect(screen.getByText('Description 2')).toBeInTheDocument();
  });

  it('should not show content initially', () => {
    render(<ExpandableSectionList sections={testSections} />);
    expect(screen.queryByText('Content 1')).not.toBeInTheDocument();
    expect(screen.queryByText('Content 2')).not.toBeInTheDocument();
  });

  it('should show content on expand', () => {
    render(<ExpandableSectionList sections={testSections} />);
    const section1Button = screen.getByText('Section 1').closest('button');
    
    fireEvent.click(section1Button!);
    expect(screen.getByText('Content 1')).toBeInTheDocument();
  });

  it('should apply custom className', () => {
    const { container } = render(
      <ExpandableSectionList
        sections={testSections}
        className="custom-list"
      />
    );
    expect(container.querySelector('.custom-list')).toBeInTheDocument();
  });

  it('should handle empty sections array', () => {
    const { container } = render(<ExpandableSectionList sections={[]} />);
    expect(container.querySelectorAll('button').length).toBe(0);
  });
});
