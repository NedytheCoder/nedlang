import type { Lesson } from "./types"
import LessonHeader from "./LessonHeader"
import LessonIntro from "./LessonIntro"
import CoreExplanation from "./CoreExplanation"
import ExampleBlock from "./ExampleBlock"
import DialogueBlock from "./DialogueBlock"
import VocabularyBlock from "./VocabularyBlock"
import ExerciseBlock from "./ExerciseBlock"
import ReinforcementBlock from "./ReinforcementBlock"
import SummaryBlock from "./SummaryBlock"

interface Props {
  lesson: Lesson
}

export default function LessonContainer({ lesson }: Props) {
  return (
    <div className="max-w-3xl mx-auto px-4 sm:px-6 lg:px-8 py-6 space-y-4">
      <LessonHeader
        title={lesson.lesson_title}
        level={lesson.level}
        topic={lesson.topic}
        framework={lesson.framework}
        progressCompleted={lesson.progress_completed}
        progressTotal={lesson.progress_total}
      />
      <LessonIntro introduction={lesson.introduction} />
      <CoreExplanation core_explanation={lesson.core_explanation} />
      {lesson.examples?.length > 0 && <ExampleBlock examples={lesson.examples} />}
      {lesson.dialogues?.length > 0 && <DialogueBlock dialogues={lesson.dialogues} lang={lesson.language_code} />}
      {lesson.vocabulary?.length > 0 && <VocabularyBlock vocabulary={lesson.vocabulary} lang={lesson.language_code} />}
      {lesson.exercises?.length > 0 && <ExerciseBlock exercises={lesson.exercises} />}
      {lesson.reinforcement && <ReinforcementBlock reinforcement={lesson.reinforcement} />}
      <SummaryBlock summary={lesson.summary} />
    </div>
  )
}
