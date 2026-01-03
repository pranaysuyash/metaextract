import React from 'react';
import type { PersonaInterpretation } from '@shared/schema';

interface PersonaDisplayProps {
  interpretation: PersonaInterpretation;
}

export const PersonaDisplay: React.FC<PersonaDisplayProps> = ({ interpretation }) => {
  if (!interpretation) {
    return null;
  }

  const { persona, key_findings, plain_english_answers } = interpretation;

  const getPersonaIcon = (personaType: string) => {
    switch (personaType) {
      case 'phone_photo_sarah':
        return '📱';
      default:
        return '👤';
    }
  };

  const getConfidenceColor = (confidence: string) => {
    switch (confidence.toLowerCase()) {
      case 'high':
        return 'text-green-600';
      case 'medium':
        return 'text-yellow-600';
      case 'low':
      case 'none':
        return 'text-red-600';
      default:
        return 'text-gray-600';
    }
  };

  const getAuthenticityIcon = (assessment: string) => {
    switch (assessment) {
      case 'appears_authentic':
        return '✅';
      case 'possibly_edited':
        return '⚠️';
      case 'likely_modified':
        return '❌';
      default:
        return '❓';
    }
  };

  return (
    <div className="persona-display bg-white rounded-lg shadow-lg p-6 mb-6">
      {/* Header */}
      <div className="flex items-center justify-between mb-4">
        <h2 className="text-2xl font-bold text-gray-800">
          {getPersonaIcon(persona)} Key Findings
        </h2>
        <span className="text-sm text-gray-500 bg-gray-100 px-3 py-1 rounded-full">
          {persona.replace('_', ' ').replace(/\b\w/g, l => l.toUpperCase())}
        </span>
      </div>

      {/* Key Findings */}
      <div className="mb-6">
        <ul className="space-y-2">
          {key_findings.map((finding, index) => (
            <li key={index} className="flex items-start text-gray-700">
              <span className="mr-2">{finding}</span>
            </li>
          ))}
        </ul>
      </div>

      {/* Sarah's Four Questions */}
      <div className="space-y-4">
        <h3 className="text-lg font-semibold text-gray-800 border-b pb-2">
          Your Questions Answered
        </h3>

        {/* When was this photo taken? */}
        <div className="bg-blue-50 rounded-lg p-4">
          <div className="flex items-center mb-2">
            <span className="text-2xl mr-3">📅</span>
            <h4 className="font-semibold text-gray-800">When was this photo taken?</h4>
          </div>
          <div className="ml-9">
            <p className="text-xl font-bold text-gray-900">
              {plain_english_answers.when_taken.answer}
            </p>
            <div className="mt-2 text-sm text-gray-600 space-y-1">
              <p><strong>Details:</strong> {plain_english_answers.when_taken.details}</p>
              <p className={getConfidenceColor(plain_english_answers.when_taken.confidence)}>
                <strong>Confidence:</strong> {plain_english_answers.when_taken.confidence}
              </p>
              <p><strong>Source:</strong> {plain_english_answers.when_taken.source}</p>
            </div>
          </div>
        </div>

        {/* Where was I when I took this? */}
        <div className="bg-green-50 rounded-lg p-4">
          <div className="flex items-center mb-2">
            <span className="text-2xl mr-3">📍</span>
            <h4 className="font-semibold text-gray-800">Where was I when I took this?</h4>
          </div>
          <div className="ml-9">
            <p className="text-xl font-bold text-gray-900">
              {plain_english_answers.location.answer}
            </p>
            <div className="mt-2 text-sm text-gray-600 space-y-1">
              <p><strong>Details:</strong> {plain_english_answers.location.details}</p>

              {plain_english_answers.location.has_location && plain_english_answers.location.coordinates && (
                <>
                  <p><strong>Coordinates:</strong> {plain_english_answers.location.coordinates.formatted}</p>
                  {plain_english_answers.location.readable_location && (
                    <p><strong>Location:</strong> {plain_english_answers.location.readable_location}</p>
                  )}
                </>
              )}

              {!plain_english_answers.location.has_location && plain_english_answers.location.possible_reasons && (
                <div className="mt-2">
                  <p><strong>Possible reasons:</strong></p>
                  <ul className="list-disc ml-5">
                    {plain_english_answers.location.possible_reasons.map((reason, index) => (
                      <li key={index}>{reason}</li>
                    ))}
                  </ul>
                </div>
              )}

              <p className={getConfidenceColor(plain_english_answers.location.confidence)}>
                <strong>Confidence:</strong> {plain_english_answers.location.confidence}
              </p>
            </div>
          </div>
        </div>

        {/* What phone took this? */}
        <div className="bg-purple-50 rounded-lg p-4">
          <div className="flex items-center mb-2">
            <span className="text-2xl mr-3">📱</span>
            <h4 className="font-semibold text-gray-800">What phone took this?</h4>
          </div>
          <div className="ml-9">
            <p className="text-xl font-bold text-gray-900">
              {plain_english_answers.device.answer}
            </p>
            <div className="mt-2 text-sm text-gray-600 space-y-1">
              <p><strong>Device Type:</strong> {plain_english_answers.device.device_type}</p>
              <p className={getConfidenceColor(plain_english_answers.device.confidence)}>
                <strong>Confidence:</strong> {plain_english_answers.device.confidence}
              </p>
              {plain_english_answers.device.details.software && (
                <p><strong>Software:</strong> {plain_english_answers.device.details.software}</p>
              )}
            </div>
          </div>
        </div>

        {/* Is this photo authentic? */}
        <div className="bg-orange-50 rounded-lg p-4">
          <div className="flex items-center mb-2">
            <span className="text-2xl mr-3">✨</span>
            <h4 className="font-semibold text-gray-800">Is this photo authentic?</h4>
          </div>
          <div className="ml-9">
            <div className="flex items-center">
              <span className="text-2xl mr-2">{getAuthenticityIcon(plain_english_answers.authenticity.assessment)}</span>
              <p className="text-xl font-bold text-gray-900">
                {plain_english_answers.authenticity.answer}
              </p>
            </div>
            <div className="mt-2 text-sm text-gray-600 space-y-1">
              <p><strong>Score:</strong> {plain_english_answers.authenticity.score}/100</p>
              <p className={getConfidenceColor(plain_english_answers.authenticity.confidence)}>
                <strong>Confidence:</strong> {plain_english_answers.authenticity.confidence}
              </p>
              <p><strong>Assessment:</strong> {plain_english_answers.authenticity.assessment.replace(/_/g, ' ')}</p>

              {plain_english_answers.authenticity.reasons && plain_english_answers.authenticity.reasons.length > 0 && (
                <div className="mt-2">
                  <p><strong>Reasons:</strong></p>
                  <ul className="list-disc ml-5">
                    {plain_english_answers.authenticity.reasons.map((reason, index) => (
                      <li key={index}>{reason}</li>
                    ))}
                  </ul>
                </div>
              )}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};