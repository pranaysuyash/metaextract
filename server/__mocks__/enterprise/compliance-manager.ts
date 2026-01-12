// Manual mock for compliance manager

export const complianceManager = {
  scheduleComplianceAudit: jest.fn(),
  handleDataSubjectAccessRequest: jest.fn(),
  reportDataBreach: jest.fn(),
  generateComplianceReport: jest.fn(),
  // add other commonly used methods as needed
};

export const ComplianceManager = jest.fn(() => complianceManager);

export default complianceManager;
